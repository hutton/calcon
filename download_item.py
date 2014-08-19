from google.appengine.ext import db

__author__ = 'simonhutton'

# Hash, BlobKey, Created Date, Date Paid, FileName, FileSize

class Download(db.Model):
    '''
    classdocs
    '''

    download = db.BooleanProperty()
    hash = db.StringProperty()
    filename = db.StringProperty()
    extension = db.StringProperty()
    file_size = db.IntegerProperty()
    time = db.FloatProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
