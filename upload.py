import json
import string
from google.appengine.api.app_identity import app_identity

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
from helper import process_calendar, log_upload, support_email, format_events_for_html
from google.appengine._internal.django.utils import simplejson
import traceback


def drop_extension_from_filename(filename):
    sp = filename.split('.')

    if len(sp) > 1:
        return string.join(sp[:-1], '.')
    else:
        return filename


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
            file_info = self.request.POST['file']

            full_filename = file_info.filename
            file_content = file_info.file.read()
            file_size = len(file_content)
            file_hash = hashlib.md5(file_content).hexdigest()

            try:
                current_conversion = self.get_conversion_from_hash(file_hash)

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

                        events = process_calendar(cal)

                        current_conversion.hash = file_hash
                        current_conversion.full_filename = full_filename
                        current_conversion.filename = drop_extension_from_filename(full_filename)
                        current_conversion.file_size = file_size
                        current_conversion.event_count = len(events)
                        current_conversion.first_ten_events = simplejson.dumps(events[:10])

                        current_conversion.blob_key = self.save_file(file_hash, file_content)

                        current_conversion.put()

                        first_ten_events = current_conversion.get_first_ten_events()

                        first_ten_events = format_events_for_html(first_ten_events)

                        response = {'message': "Calendar created.",
                                    'paid': not current_conversion.paid_date is None,
                                    'filename': current_conversion.filename,
                                    'full_filename': current_conversion.full_filename,
                                    'event_count': current_conversion.event_count,
                                    'todo_count': current_conversion.todo_count,
                                    'key': current_conversion.hash,
                                    'events': first_ten_events}

                        log_upload(current_conversion, time.time() - start_time)
                    else:
                        # Not a valid iCalendar
                        response = {'message': "That's not a valid iCalendar file.",
                                    'filename': None,
                                    'paid': False,
                                    'key': None}

                        self.response.status = 500
                else:
                    filename = drop_extension_from_filename(full_filename)

                    if current_conversion.full_filename != full_filename or current_conversion.filename != filename:
                        current_conversion.full_filename = full_filename
                        current_conversion.filename = filename

                        current_conversion.put()

                    first_ten_events = format_events_for_html(current_conversion.get_first_ten_events())

                    response = {'message': "Exisiting calendar.",
                                'paid': not current_conversion.paid_date is None,
                                'filename': current_conversion.filename,
                                'full_filename': current_conversion.full_filename,
                                'event_count': current_conversion.event_count,
                                'todo_count': current_conversion.todo_count,
                                'key': current_conversion.hash,
                                'events': first_ten_events}

                    log_upload(current_conversion, time.time() - start_time)
            except Exception, e:
                trace = traceback.format_exc()

                logging.error('Exception while tyring to upload.')
                logging.error(e.message)
                logging.error(trace)

                email_message = e.message + '\r\n\r\n' + trace

                support_email('Upload Failed', email_message)

                response = {'message': "Something bad happened, we're looking at it."}

                self.response.status = 500
        else:
            response = {'message': "Something bad happened, we're looking at it."}

            logging.error(self.request.params.multi)

            if len(self.request.params.multi) > 0:
                support_email('Upload Failed', str(self.request.params.multi))

            self.response.status = 500

        self.response.out.write(simplejson.dumps(response))

