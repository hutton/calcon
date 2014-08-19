import string
from google.appengine.api.app_identity import app_identity
from google.appengine.ext import db
import time

__author__ = 'simonhutton'

import sys

sys.path.insert(0, 'libs')

import conversion

import webapp2

import icalendar
import hashlib
from google.appengine.ext import blobstore
import logging
import cloudstorage as gcs
from helper import process_calendar, log_upload
from google.appengine._internal.django.utils import simplejson

def drop_extension_from_filename(filename):
    sp = filename.split('.')

    if len(sp) > 1:
        return string.join(sp[:-1], '.')
    else:
        return filename


class Upload(webapp2.RequestHandler):
    @staticmethod
    def get_conversion_from_hash_and_full_filename(file_hash, original_filename):
        query = conversion.Conversion.gql("WHERE hash = :hash AND full_filename = :original_filename", hash=file_hash,
                                          original_filename=original_filename)
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
            file_info = self.request.POST['file']

            full_filename = file_info.filename
            file_content = file_info.file.read()
            file_size = len(file_content)
            file_hash = hashlib.md5(file_content).hexdigest()

            current_conversion = self.get_conversion_from_hash_and_full_filename(file_hash, full_filename)

            start_time = time.time()

            if not current_conversion:
                # noinspection PyBroadException
                try:
                    cal = icalendar.Calendar.from_ical(file_content)
                except Exception, e:
                    cal = None
                    logging.info('File ' + full_filename + ' was not a valid calendar')

                if cal:
                    current_conversion = conversion.Conversion()

                    events, todos = process_calendar(cal)

                    current_conversion.hash = file_hash
                    current_conversion.full_filename = full_filename
                    current_conversion.filename = drop_extension_from_filename(full_filename)
                    current_conversion.file_size = file_size
                    current_conversion.event_count = len(events)
                    current_conversion.todo_count = len(todos)

                    current_conversion.blob_key = self.save_file(file_hash, file_content)

                    db.put(current_conversion)

                    response = {'message': "Calendar created.",
                                'paid': not current_conversion.paid_date is None,
                                'filename': current_conversion.filename,
                                'full_filename': current_conversion.full_filename,
                                'event_count': current_conversion.event_count,
                                'todo_count': current_conversion.todo_count,
                                'key': current_conversion.hash}

                    log_upload(current_conversion, time.time() - start_time)
                else:
                    # Not a valid iCalendar
                    response = {'message': "That's not a valid iCalendar file.",
                                'filename': None,
                                'paid': False,
                                'key': None}

                    self.response.status = 500
            else:
                response = {'message': "Exisiting calendar.",
                            'paid': not current_conversion.paid_date is None,
                            'filename': current_conversion.filename,
                            'full_filename': current_conversion.full_filename,
                            'event_count': current_conversion.event_count,
                            'todo_count': current_conversion.todo_count,
                            'key': current_conversion.hash}

                log_upload(current_conversion, time.time() - start_time)

        self.response.out.write(simplejson.dumps(response))

