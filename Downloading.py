import sys

sys.path.insert(0, 'libs')

import re
import webapp2
import conversion
from google.appengine.ext import blobstore
import tablib
import icalendar

__author__ = 'simonhutton'


def process_calendar(calendar):
    events = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {'Summary': component.get('summary'),
                     'Description': component.get('description'),
                     'Start': component.get('dtstart').dt,
                     'End': component.get('dtend').dt,
                     'Created': component.get('dtstamp').dt}

            events.append(event)

    return events


def build_tab_lib_dataset(events):
    data = tablib.Dataset()
    for event in events:
        data.append([event['Summary'], str(event['Description'])])
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

            current_conversion = self.get_conversion_from_hash(file_hash)

            if current_conversion:
                file_content = blobstore.fetch_data(current_conversion.blob_key, 0, current_conversion.file_size)

                gcal = icalendar.Calendar.from_ical(file_content)

                events = process_calendar(gcal)
                
                if extension == 'csv':
                    self.response.headers['Content-Type'] = 'application/csv'
                    output_content = generate_csv_content(events)

                if extension == 'xls':
                    self.response.headers['Content-Type'] = 'application/xls'
                    output_content = generate_xls_content(events)

        self.response.out.write(output_content)
