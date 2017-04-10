from datetime import datetime, timedelta
from pytz import timezone
from shutil import copyfile
import requests
import json
import time
import pytz
import os

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

    @property
    def dictionary(self):
        d = self.__dict__
        d["when"] = self.when()
        d["length"] = self.length()
        return d

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

def generate_post_filename(event, zone):
    """Generates the filename for the event's post"""
    return event.when(zone).strftime("%B-%Y-meetup.md")

def get_template_path(template_name):
    """Get the path to the template file that will be copied"""
    return os.path.join("./scaffolds", template_name + ".md")

def generate_post(template, destination_folder, event, zone):
    """Generates event post file"""

    # Create initial post from template
    file_name = generate_post_filename(event, zone)
    full_file_name = destination_folder + "/" + file_name
    copyfile(template, full_file_name)

    # Process placeholders
    content = ""
    values = event.dictionary
    with open(full_file_name, mode="r") as post_file:
        for line in post_file:
            content += line.format(**values)

    # Saving processed content
    with open(full_file_name, mode="w") as post_file:
        for line in content:
            post_file.write(line)

if __name__ == "__main__":
    MEETUP_ROOT = "https://api.meetup.com"
    GROUP_NAME = "OKC-sharp"
    MEETUP_APIKEY = "64324f6535207f355a781133296f6a22"
    group_timezone = "US/Central"

    next_event = get_next_event(MEETUP_APIKEY, MEETUP_ROOT, GROUP_NAME)
    template_path = get_template_path("meetup")
    generate_post(template_path, "source/_posts", next_event, timezone(group_timezone))

    #print("Hello {when}".format(**next_event.dictionary))
    #print(next_event.dictionary["when"])
