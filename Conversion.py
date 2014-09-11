import sys
import json
sys.path.insert(0, 'libs')

from google.appengine.ext import db

from google.appengine.ext import blobstore

import icalendar
from helper import process_calendar
from google.appengine._internal.django.utils import simplejson

__author__ = 'simonhutton'

# Hash, BlobKey, Created Date, Date Paid, FileName, FileSize

class Conversion(db.Model):
    '''
    classdocs
    '''

    hash = db.StringProperty()
    blob_key = db.BlobProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    paid_date = db.DateTimeProperty()
    filename = db.StringProperty()
    file_size = db.IntegerProperty()
    full_filename = db.StringProperty()
    event_count = db.IntegerProperty()
    todo_count = db.IntegerProperty()
    first_ten_events = db.TextProperty()

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
            
