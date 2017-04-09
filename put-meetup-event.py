from datetime import datetime, timedelta
from pytz import timezone
import requests
import json
import time
import pytz

class Event(object):
    def __init__(self, id, name, time, duration, description, updated, venue_name, **kwargs):
        self.id = id
        self.name = name
        self.time = time
        self.duration = duration
        self.description = description
        self.updated = updated
        self.venue_name = venue_name

    def __repr__(self):
        return json.dumps(self.__dict__)

    def _localize(self, the_time, zone=None):
        if zone is None:
            zone = pytz.utc
        utc = datetime.fromtimestamp(the_time)
        return zone.localize(utc)

    def when(self, time_zone=None):
        return self._localize(self.time, time_zone)

    def modified(self, time_zone=None):
        return self._localize(self.updated, time_zone)

    def length(self):
        return timedelta(milliseconds=self.duration)

def get_next_event(api_key, api_root, group_name):
    """Returns the next meetup event."""
    url = "{0}/{1}/events".format(api_root, group_name)
    params = {
        "scroll": "next_upcoming",
        "page": "1",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()[0]

    data["time"] = data["time"] / 1000 # MeetUp gives timestamp in milliseconds
    data["updated"] = data["updated"] / 1000 # MeetUp gives timestamp in milliseconds

    event = Event(venue_name=data["venue"]["name"], **data)
    return event

if __name__ == "__main__":
    root = "https://api.meetup.com"
    group = "OKC-sharp"
    key = "64324f6535207f355a781133296f6a22"
    zone = "US/Central"
    next_event = get_next_event(key, root, group)
    #print(next_event)

    print(next_event)
