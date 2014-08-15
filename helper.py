import sys

sys.path.insert(0, 'libs')

import icalendar

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
