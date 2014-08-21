import os
import sys
import time
from helper import process_calendar, log_download

sys.path.insert(0, 'libs')

import re
import webapp2
import conversion
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
import tablib
import icalendar

__author__ = 'simonhutton'

column_order = ['Summary', 'Description', 'Start', 'End', 'Organizer', 'Attendees', 'Location', 'Created']


def order_columns(column_name, keys):
    return column_name in keys


def build_tab_lib_dataset(events):
    data = tablib.Dataset()

    keys = list(set([key for event in events for key in event.keys()]))

    ordered_columns = [item for item in column_order if order_columns(item, keys)]

    rows = [[event.get(key, '') for key in ordered_columns] for event in events]

    data.headers = ordered_columns

    for row in rows:
        data.append(row)

    return data


def generate_csv_content(events):
    data = build_tab_lib_dataset(events)

    return data.csv


def generate_xls_content(events):
    data = build_tab_lib_dataset(events)

    return data.xls


def generate_xlsx_content(events):
    data = build_tab_lib_dataset(events)

    return data.xlsx


def generate_json_content(events):
    data = build_tab_lib_dataset(events)

    return data.json


def generate_tsv_content(events):
    data = build_tab_lib_dataset(events)

    return data.tsv


def generate_txt_content(events):

    path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/txt_template.txt')

    return template.render(path, {'events': events})


def generate_xml_content(events):

    path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/xml_template.xml')

    return template.render(path, {'events': events})


def generate_html_content(events):

    path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/html_template.html')

    return template.render(path, {'events': events})


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
            r"/download/(?P<hash>[0-9a-z]+)/(?P<filename>[-\w^&'@{}[\],$=!#().%+~ ]+).(?P<extension>txt|csv|xls|xlsx|json|tsv|xml|html)",
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

                if extension == 'xlsx':
                    self.response.headers['Content-Type'] = 'application/xlsx'
                    output_content = generate_xlsx_content(events)

                if extension == 'json':
                    self.response.headers['Content-Type'] = 'application/json'
                    output_content = generate_json_content(events)

                if extension == 'tsv':
                    self.response.headers['Content-Type'] = 'application/tsv'
                    output_content = generate_tsv_content(events)

                if extension == 'txt':
                    self.response.headers['Content-Type'] = 'application/txt'
                    output_content = generate_txt_content(events)

                if extension == 'xml':
                    self.response.headers['Content-Type'] = 'application/xml'
                    output_content = generate_xml_content(events)

                if extension == 'html':
                    self.response.headers['Content-Type'] = 'application/html'
                    output_content = generate_html_content(events)

                log_download(current_conversion, time.time() - start_time, extension)

                self.response.out.write(output_content)
                return

        self.response.status = 404
