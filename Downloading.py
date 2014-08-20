import sys
import time
from helper import process_calendar, log_download

sys.path.insert(0, 'libs')

import re
import webapp2
import conversion
from google.appengine.ext import blobstore
import tablib
import icalendar

__author__ = 'simonhutton'


def build_tab_lib_dataset(events):
    data = tablib.Dataset()

    keys = list(set([key for event in events for key in event.keys()]))

    rows = [[event.get(key, '') for key in keys] for event in events]

    data.headers = keys

    for row in rows:
        data.append(row)

    return data


def generate_csv_content(events):
    data = build_tab_lib_dataset(events)

    return data.csv


def generate_xls_content(events):
    data = build_tab_lib_dataset(events)

    return data.xls


class Downloading(webapp2.RequestHandler):
    @staticmethod
    def get_conversion_from_hash(file_hash):
        query = conversion.Conversion.gql("WHERE hash = :hash", hash=file_hash)
        conversions = query.fetch(1)
        if conversions:
            return conversions[0]
        else:
            return None

    def get(self):

        matches = re.match(
            r"/download/(?P<hash>[0-9a-z]+)/(?P<filename>[-\w^&'@{}[\],$=!#().%+~ ]+).(?P<extension>txt|csv|xls)",
            self.request.path)

        if matches:
            file_hash = matches.group("hash")
            filename = matches.group("filename")
            extension = matches.group("extension")

            start_time = time.time()

            current_conversion = self.get_conversion_from_hash(file_hash)

            if current_conversion:
                blob_reader = blobstore.BlobReader(current_conversion.blob_key)

                file_content = blob_reader.read()

                gcal = icalendar.Calendar.from_ical(file_content)

                events = process_calendar(gcal)
                
                if extension == 'csv':
                    self.response.headers['Content-Type'] = 'application/csv'
                    output_content = generate_csv_content(events)

                if extension == 'xls':
                    self.response.headers['Content-Type'] = 'application/xls'
                    output_content = generate_xls_content(events)

                log_download(current_conversion, time.time() - start_time, extension)

                self.response.out.write(output_content)
                return

        self.response.status = 404
