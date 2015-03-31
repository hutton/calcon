import sys
import json
sys.path.insert(0, 'libs')

from google.appengine.ext import ndb

from google.appengine.ext import blobstore

import icalendar
from helper import process_calendar
from google.appengine._internal.django.utils import simplejson

__author__ = 'simonhutton'

# Hash, BlobKey, Created Date, Date Paid, FileName, FileSize

class Conversion(ndb.Model):
    '''
    classdocs
    '''

    hash = ndb.StringProperty()
    blob_key = ndb.BlobProperty()
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    paid_date = ndb.DateTimeProperty()
    filename = ndb.StringProperty()
    file_size = ndb.IntegerProperty()
    full_filename = ndb.StringProperty()
    event_count = ndb.IntegerProperty()
    todo_count = ndb.IntegerProperty()
    first_ten_events = ndb.TextProperty()

    def get_events(self):
        blob_reader = blobstore.BlobReader(self.blob_key)

        file_content = blob_reader.read()

        converted_calendar = icalendar.Calendar.from_ical(file_content)

        return process_calendar(converted_calendar)

    def get_first_ten_events(self):
        if self.first_ten_events:
            return json.loads(str(self.first_ten_events))
        else:
            events = self.get_events()
    
            first_ten = events[:10]

            self.first_ten_events = simplejson.dumps(first_ten)
    
            self.put()

            return first_ten