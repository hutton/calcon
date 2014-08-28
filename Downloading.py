import StringIO
import logging
import os
import sys
import time
from google.appengine.api import memcache
from xhtml2pdf import pisa
from helper import process_calendar, log_download

sys.path.insert(0, 'libs')

import re
import webapp2
import conversion
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
import tablib
import icalendar
from google.appengine._internal.django.utils import simplejson

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


def generate_html_content(events, filename):
    path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/html_template.html')

    return template.render(path, {'events': events, 'filename': filename})


def generate_pdf_content(events, filename):
    path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/pdf_template.html')

    html_output = template.render(path, {'events': events, 'filename': filename})

    pdf_output = StringIO.StringIO()

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(html_output, dest=pdf_output)

    if pisa_status.err:
        logging.error('Failed to covert to pdf')
        raise

    pdf_output.seek(0)

    return pdf_output.getvalue()


class DownloadProgress(webapp2.RequestHandler):
    def get(self):
        download_id = self.request.get('downloadId')

        data = memcache.get(download_id)

        retry = True

        start_time = time.time()

        while (data or retry) and time.time() - start_time < 60:
            data = memcache.get(download_id)
            retry = False
            time.sleep(0.5)

        if data:
            logging.warning('Timeout waiting for: ' + download_id)

        self.response.status = 200

        response = {'message': 'finished'}

        self.response.out.write(simplejson.dumps(response))


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
            r"/download/(?P<hash>[0-9a-z]+)/(?P<filename>[-\w^&'@{}[\],$=!#().%+~ ]+).(?P<extension>txt|csv|xlsx|xls|json|tsv|xml|html|pdf)",
            self.request.path)

        if matches:
            file_hash = matches.group("hash")
            filename = matches.group("filename")
            extension = matches.group("extension")

            download_id = file_hash + '_' + filename + '.' + extension

            memcache.add(download_id, 'Downloading', 120)

            start_time = time.time()

            current_conversion = self.get_conversion_from_hash(file_hash)

            if current_conversion:
                blob_reader = blobstore.BlobReader(current_conversion.blob_key)

                file_content = blob_reader.read()

                gcal = icalendar.Calendar.from_ical(file_content)

                events = process_calendar(gcal)

                if extension == 'csv':
                    self.response.headers['Content-Type'] = 'application/x-unknown'
                    self.response.headers['Content-Disposition'] = 'attachment; filename=' + filename + '.' + extension + ''
                    self.response.headers['Content-Transfer-Encoding'] = 'binary'
                    self.response.headers['Content-Length'] = current_conversion.file_size
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
                    output_content = generate_html_content(events, filename + '.' + extension)

                if extension == 'pdf':
                    self.response.headers['Content-Type'] = 'application/pdf'
                    output_content = generate_pdf_content(events, filename + '.' + extension)

                log_download(current_conversion, time.time() - start_time, extension)

                memcache.delete(download_id)

                self.response.out.write(output_content)
                return

        self.response.status = 404
