import sys

sys.path.insert(0, 'libs')

import icalendar

def process_calendar(calendar):
    events = []
    todos = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {'Summary': component.get('summary'),
                     'Description': component.get('description'),
                     'Start': component.get('dtstart').dt,
                     'End': component.get('dtend').dt,
                     'Created': component.get('dtstamp').dt}

            events.append(event)

    return events, todos
