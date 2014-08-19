import sys
import download_item

sys.path.insert(0, 'libs')

import icalendar
from google.appengine.ext import db


def try_get_date_field(component, field):
    value = component.get(field)

    if value:
        return value.dt

    return None


def process_calendar(calendar):
    events = []
    todos = []

    for component in calendar.walk():
        if component.name == "VEVENT":

            event = {'Summary': unicode(component.get('summary')),
                     'Description': unicode(component.get('description')),
                     'Start': try_get_date_field(component, 'dtstart'),
                     'End': try_get_date_field(component, 'dtend'),
                     'Created': try_get_date_field(component, 'dtstamp')}

            events.append(event)

    return events, todos


def log_upload(current_conversion, time):
    new_upload = download_item.Download()

    new_upload.download = False
    new_upload.hash = current_conversion.hash
    new_upload.filename = current_conversion.full_filename
    new_upload.file_size = current_conversion.file_size
    new_upload.time = time

    db.put(new_upload)

def log_download(current_conversion, time):
    new_download = download_item.Download()

    new_download.download = True
    new_download.hash = current_conversion.hash
    new_download.filename = current_conversion.full_filename
    new_download.file_size = current_conversion.file_size
    new_download.time = time

    db.put(new_download)
