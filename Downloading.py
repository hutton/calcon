import re
import webapp2

__author__ = 'simonhutton'


class Downloading(webapp2.RequestHandler):
    def get(self):

        matches = re.match(r"/download/([0-9a-z]*)/([0-9a-z]*).([a-z]*)", self.request.path)

        self.response.out.write("read")
