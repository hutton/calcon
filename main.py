#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import sys

from google.appengine.api import app_identity
from google.appengine.ext import db

import conversion


sys.path.insert(0, 'libs')

import os
from google.appengine._internal.django.utils import simplejson
from google.appengine.ext.webapp import template
import webapp2
import cloudstorage as gcs

import icalendar
import xlsxwriter
import hashlib
from google.appengine.ext import blobstore

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/main.html')
        self.response.out.write(template.render(path, {}))


class Upload(webapp2.RequestHandler):
    @staticmethod
    def get_conversion_from_hash(file_hash):
        query = conversion.Conversion.gql("WHERE hash = :hash", hash=file_hash)
        conversions = query.fetch(1)
        if conversions:
            return conversions[0]
        else:
            return None

    @staticmethod
    def save_file(file_hash, file_content):
        blob_filename = '/%s/%s/%s' % (app_identity.get_default_gcs_bucket_name(), 'ics', file_hash)
        with gcs.open(blob_filename, 'w') as f:
            f.write(file_content)

        blob_store_filename = '/gs' + blob_filename
        return blobstore.create_gs_key(blob_store_filename)

    def post(self):

        if len(self.request.params.multi.dicts) > 1 and 'file' in self.request.params.multi.dicts[1]:
            file_info = self.request.params.multi.dicts[1]['file']

            filename = file_info.filename
            file_content = file_info.file.read()
            file_size = len(file_content)
            file_hash = hashlib.md5(file_content).hexdigest()

            current_conversion = self.get_conversion_from_hash(file_hash)

            if not current_conversion:
                # noinspection PyBroadException
                try:
                    cal = icalendar.Calendar.from_ical(file_content)
                except Exception, e:
                    cal = None
                    logging.info('File ' + filename + ' was not a valid calendar')

                if cal:
                    current_conversion = conversion.Conversion()

                    current_conversion.hash = file_hash
                    current_conversion.filename = filename
                    current_conversion.file_size = file_size

                    current_conversion.blob_key = self.save_file(file_hash, file_content)

                    db.put(current_conversion)

                    response = {'message': "Calendar created.",
                                'paid': not current_conversion.paid_date is None,
                                'key': current_conversion.hash}
                else:
                    # Not a valid iCalendar
                    response = {'message': "Not a valid calendar.",
                                'paid': False,
                                'key': None}
            else:
                response = {'message': "Exisiting calendar.",
                            'paid': not current_conversion.paid_date is None,
                            'key': current_conversion.hash}

        self.response.out.write(simplejson.dumps(response))


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', Upload)], debug=True)
