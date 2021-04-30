import os
import sys
import time
import argparse
import configparser
import numpy
import json
import click

from abc import abstractmethod, ABC
from datetime import date, datetime, timedelta
from collections import defaultdict
from progressbar import ProgressBar, Timer
from matplotlib import pyplot
from collections import OrderedDict
from typing import Optional, Union, List
from configparser import ConfigParser

track_file = os.path.expanduser("~/.timetrack_log")


class TimerException(Exception):
    """Exception thrown when something goes wrong with timer"""

class TTBaseDriver(ABC):
    
    @abstractmethod
    def delete_entry(self, entry_id):
        """Remove entry from timetrack container"""

    @abstractmethod
    def add_entry(self, project: str, time, comment: Union[str, List[str]], when: Union[str, datetime, None] = datetime.now()):
        """Add a new timetrack entry"""

    @abstractmethod
    def update_entry(self, entry_id, time):
        """Update time for given entry id"""

    @abstractmethod
    def get_filtered_entries(self, start=None, finish=None, project=None):
        """Return a filtered set of entries"""
        
    @abstractmethod
    def get_projects(self):
        """Return known project list"""
        
    @abstractmethod
    def get_tasks(self, project=None):
        """Return task types from projects"""
        
class TTFileDriverException(Exception):
    """Exception raised by file driver"""

class TTFileDriver(TTBaseDriver):

    def __init__(self, config: ConfigParser, rootsection: Optional[str] = "driver"):
        
        self.track_file = config.get(rootsection, "track_file")
        
        if self.track_file is None:
            raise TTFileDriverException

    def add_entry(self, project, time, comment, when=None, task=None):
        """add new entry to file"""

        time = parse_time(time)

        if time < 1:
            raise TimerException("You must spend at least a minute on a task to record it.")

        if(when == None):
            day = date.today()
        elif type(when) is datetime:
            day = when.date()
        else:
            dt = datetime.strptime(when, "%Y-%m-%d")
            day = date(dt.year, dt.month, dt.day)

        if type(comment) is list:
            comment = ' '.join(comment)

        with open(self.track_file, "a") as f:
            record = {"date": day.strftime("%Y-%m-%d"), "project":project, "time": time, "comment":comment }
            
            if task is not None:
                record['task'] = task
            
            f.write("{}\n".format(json.dumps(record)))

    def delete_entry(self, entry_id):

        line = int(entry_id) - 1

        all_data = []
        found = False

        with open(self.track_file, "r") as f:
            for lineno, x in enumerate(f):
                if lineno != line:
                    all_data.append(x)
                else:
                    found = True

        with open(self.track_file, "w") as f:
            for line in all_data:
                f.write(line)

        return found

    def update_entry(self, entry_id, time):
        """Find an entry, update its time, rewrite file."""

        # identify the line to be updated
        line = int(entry_id) - 1

        all_data = []
        record = None

        # read all the data from the log into memory
        with open(self.track_file, "r") as f:
            for lineno, x in enumerate(f):
                if lineno != line:
                    all_data.append(x)
                else:
                    record = json.loads(x)

        # if after reading everything we didn't find the line, return error
        if record is None:
            print("Could not find entry with ID {}. Giving up.".format(entry_id))
            return

        # run live timer or parse updated time
        time_add = parse_time(time)

        # check time added was not less than 1 minute
        if time_add == 1:
            print("You must spend at least another minute \
                on this task to update it.")
            return

        # add updated time to total
        record['time'] += time_add

        print("Appending {} minutes to entry {} ({})".format(time_add, entry_id,
                                                            record['project']))

        # inject line into data
        entry = json.dumps(record) + "\n"

        all_data.insert(line, entry)

        # write data to file
        with open(self.track_file, "w") as f:
            for line in all_data:
                f.write(line)

    def get_filtered_entries(self, start=None, finish=None, project=None, task=None):

        with open(self.track_file, "r") as f:
            for lineno, line in enumerate(f):
                record = json.loads(line)

                dt = datetime.strptime(record['date'], "%Y-%m-%d")
                record_date = date(dt.year, dt.month, dt.day)

                if start != None and record_date < start:
                    continue

                if finish != None and record_date > finish:
                    continue

                if project != None and record['project'] != project:
                    continue
                
                if task != None and record.get('task') != task:
                    continue

                #add record ID which is just the line number +1
                record['id'] = lineno + 1
                yield record
                
    def get_projects(self):
        """Return list of known projects"""
        
        projects = set()
        
        with open(self.track_file, "r") as f:
            for line in f:
                record = json.loads(line)
                projects.add(record['project'])
        
        return projects

    def get_tasks(self, project=None):
        
        tasks = set()
        
        with open(self.track_file, "r") as f:
            for line in f:
                record = json.loads(line)
                if 'task' in record and (project is None or record['project'] == project):
                    tasks.add(record.get('task'))
            
        return tasks
                    



def load_config():
    """Load config variables for timetrack"""

    config = configparser.ConfigParser()
    config['timetrack'] = {"working_hours": 10}
    config['driver'] = {
        "type":"file",
        "track_file": os.path.expanduser("~/.timetrack_log")
    }

    confpath = os.path.expanduser("~/.timetrack")

    if not os.path.exists(confpath):
        print("Config file does not exist. Creating default one")
        with open(confpath, "w") as f:
            config.write(f)
    else:
        config.read(confpath)

    return config


def parse_time(time):
    """Given the time string, parse and turn into normalised minute count"""

    if type(time) in [int,float]:
        return time

    if time.endswith('m'):
        time = time[0:-1]

    if time.find('h') != -1:
        time = time.replace('h', ':')

    if time.find(':') != -1:
        hours, minutes = time.split(':')

        if minutes.strip() == "":
            minutes = 0

    else:
        hours = 0
        minutes = int(time.strip())

    total = int(minutes) + (int(hours) * 60)

    return total



def human_time(minutes):
    """Returns x hours y minutes for an input of minutes"""

    minutes = int(minutes)
    hours = minutes // 60
    mins = minutes % 60

    return "{}h{}m".format(hours, mins)


def day_spent(records):
    """Return the total time spent for given day"""
    return sum([int(record['time']) for record in records])

def day_remainder(records, working_hours=10):
    """Calculate how much of your day is unspent"""

    day_minutes = int(working_hours) * 60
    total_spent = day_spent(records)

    return day_minutes - total_spent
