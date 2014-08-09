from google.appengine.ext import db

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
