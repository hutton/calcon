import sys
import download_item

sys.path.insert(0, 'libs')

import icalendar
from google.appengine.ext import db


def add_text_field(component, component_name, dict, dict_name):

    value = component.get(component_name)

    if value:
        dict[dict_name] = unicode(value)


def add_date_field(component, component_name, dict, dict_name):
    value = component.get(component_name)

    if value:
        dict[dict_name] = value.dt


def process_calendar(calendar):
    events = []
    todos = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {}

            add_text_field(component, 'summary', event, 'Summary')
            add_text_field(component, 'description', event, 'Description')
            add_date_field(component, 'dtstart', event, 'Start')
            add_date_field(component, 'dtend', event, 'End')
            add_date_field(component, 'created', event, 'Created')

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

def log_download(current_conversion, time, extension):
    new_download = download_item.Download()

    new_download.download = True
    new_download.hash = current_conversion.hash
    new_download.filename = current_conversion.full_filename
    new_download.file_size = current_conversion.file_size
    new_download.time = time
    new_download.extension = extension

    db.put(new_download)
