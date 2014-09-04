from datetime import date, datetime, time, timedelta
import os
from google.appengine.ext.webapp import template
import webapp2
from download_item import Download
from google.appengine._internal.django.utils import simplejson

__author__ = 'simonhutton'


def extract_data(items):
    uploads = [download for download in items if not download.download]
    downloads = [download for download in items if download.download]

    file_types = ['csv', 'xslx', 'html', 'xml', 'pdf', 'json', 'txt', 'tsv']

    file_type_frequencies = [len([download for download in items if download.extension == extension]) for extension in
                             file_types]

    return {'uploads': len(uploads),
            'downloads': len(downloads),
            'fileTypeFrequencies': file_type_frequencies}


class Statistics(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.join(os.path.dirname(__file__), 'html'), '../templates/stats.html')
        self.response.out.write(template.render(path, {}))


class StatisticsData(webapp2.RequestHandler):
    def get(self):
        today = datetime.combine(date.today(), time())
        month_ago = today - timedelta(days=30)

        query = Download.all()

        all_downloads = query.fetch(None)

        # all_downloads = []

        today_items = [download for download in all_downloads if download.created_date > today]
        month_items = [download for download in all_downloads if download.created_date > month_ago]

        today_values = extract_data(today_items)
        today_values['title'] = "Today"

        month_values = extract_data(month_items)
        month_values['title'] = "Month"

        all_values = extract_data(all_downloads)
        all_values['title'] = "All"

        response = [today_values,
                    month_values,
                    all_values]

        self.response.out.write(simplejson.dumps(response))


