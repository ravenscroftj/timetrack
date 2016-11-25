import os
import sys
import time
import argparse
import configparser
import numpy
from datetime import date, datetime, timedelta
from collections import defaultdict
from progressbar import ProgressBar, Timer
from matplotlib import pyplot

track_file = os.path.expanduser("~/.timetrack_log")
working_hours = 10


def load_config():
    """Load config variables for timetrack"""
    global working_hours, track_file

    config = configparser.ConfigParser()
    config['timetrack'] = {"track_file": os.path.expanduser(
                                             "~/.timetrack_log"),
                           "working_hours": 10}

    confpath = os.path.expanduser("~/.timetrack")

    if not os.path.exists(confpath):
        print("Config file does not exist. Creating default one")
        with open(confpath, "w") as f:
            config.write(f)
    else:
        config.read(confpath)

    working_hours = config['timetrack']['working_hours']
    track_file = config['timetrack']['track_file']


def delete(args):
    """Remove a chunk of time from the log"""

    line = int(args.line) - 1

    all_data = []

    with open(track_file, "r") as f:
        for lineno, x in enumerate(f):
            if lineno != line:
                all_data.append(x)

    with open(track_file, "w") as f:
        for line in all_data:
            f.write(line)

    args.week = False
    args.month = False
    list_logs(args)


def add(args):
    """Add a chunk of time to the report."""
    global track_file

    if args.time == "live":
        time = int(live_time(args))
    else:
        time = parse_time(args.time)

    if time < 1:
        print("You must spend at least a minute on a task to record it.")
        return

    if(args.when == "now"):
        day = date.today()
    else:
        dt = datetime.strptime(args.when, "%Y-%m-%d")
        day = date(dt.year, dt.month, dt.day)

    comment = ' '.join(args.comment)

    print("Adding {} minutes to {} project".format(time, args.project))

    with open(track_file, "a") as f:
        f.write("{}\t{}\t{}\t{}\n".format(
            day.strftime("%Y-%m-%d"),
            args.project,
            time,
            comment.replace("\t", "").replace("\n", "")))

def parse_time(time):
    """Given the time string, parse and turn into normalised minute count"""

    if time.endswith('m'):
        time = time[0:-1]

    if time.find('h') != -1:
        time = time.replace('h', ':')

    if time.find(':') != -1:
        hours,minutes = time.split(':')

        if minutes.strip() == "":
            minutes = 0

    else:
        hours = 0
        minutes = int(time.strip())

    total = int(minutes) + (int(hours) * 60)

    return total


def live_time(args):
    """Run a timer actively in the window"""
    start = datetime.now()

    print("Starting timer, press Ctrl + C at any time to end recording...")

    running = True

    widgets = ['Project:{} '.format(args.project), Timer(), '']

    with ProgressBar(widgets=widgets) as pbar:
        while(running):
            try:
                time.sleep(1)
                pbar.update(0)
            except:
                running = False

    end = datetime.now()

    diff = end - start

    return (int(diff.total_seconds()) / 60)


def human_time(minutes):
    """Returns x hours y minutes for an input of minutes"""

    minutes = int(minutes)
    hours = minutes // 60
    mins = minutes % 60

    return "{}h{}m".format(hours, mins)


def day_spent(records):
    """Return the total time spent for given day"""
    return sum([int(record[2]) for record in records])

def day_remainder(records):
    """Calculate how much of your day is unspent"""
    global working_hours

    day_minutes = int(working_hours) * 60
    total_spent = day_spent(records)

    return day_minutes - total_spent


def project_report(start,finish,echo=True):
    """Summarise total time spent per project instead of per day"""
    projects = defaultdict(lambda: 0)

    with open(track_file, "r") as f:
        for lineno, line in enumerate(f):
            datestr, project, time, comment = line.split("\t")
            dt = datetime.strptime(datestr, "%Y-%m-%d")
            record_date = date(dt.year, dt.month, dt.day)

            if record_date >= start and record_date <= finish:
                projects[project] += int(time)

    if echo:

        print("\nProject Breakdown: {} to {} \n----------".format(
            start.strftime("%Y-%m-%d"),
            finish.strftime("%Y-%m-%d")))

        for project, spent in projects.items():
            print("{}: {}".format(project, human_time(spent)))

    return projects


def report_generate(start, finish, echo=True):
    """Generate a list of items that have been tracked for given timeframe. """
    day_records = defaultdict(lambda: [])

    with open(track_file, "r") as f:
        for lineno, line in enumerate(f):
            datestr, project, time, comment = line.split("\t")
            dt = datetime.strptime(datestr, "%Y-%m-%d")
            record_date = date(dt.year, dt.month, dt.day)

            if record_date >= start and record_date <= finish:
                day_records[record_date].append((lineno, project,
                                                 time,
                                                 comment.strip()))

    if echo:  # only print if echo is on
        for day in sorted(day_records):
            records = day_records[day]

            print("\n{}\n---------".format(day.strftime("%Y-%m-%d")))
            for i, record in enumerate(records):
                print("{}) {} on {}: {}".format(record[0]+1,
                                                human_time(record[2]),
                                                record[1],
                                                record[3]))

    return day_records


def list_logs(args):
    """Show tasks recorded and time remaining today."""
    start_date, end_date = parse_time_args(args)

    records = report_generate(start_date, end_date)

    print("-----------")

    print("Time spent today: {}".format(
        human_time(day_spent(records[date.today()]))))
    print("Remaining time today: {}".format(
        human_time(day_remainder(records[date.today()]))))

def parse_time_args(args):
    """"Parses week or month args or uses today by default."""
    if args.week:
        end = datetime.now()
        delta = timedelta(days=7)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    elif args.month:
        end = datetime.now()
        delta = timedelta(days=30)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    else:
        start_date = date.today()
        end_date = date.today()

    return start_date, end_date


def report(args, echo=True):
    """Generate a report for the given timeframe."""
    start_date, end_date = parse_time_args(args)
    project_report(start_date, end_date, echo)

def report_graph(args):
    """Generate a bar chart report for the given timeframe."""
    start_date, end_date = parse_time_args(args)
    report_data = project_report(start_date, end_date, False)
    
    fig = pyplot.figure()
    fig.suptitle("Project Breakdown: {} to {}".format(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")),
            fontsize=14, fontweight='bold')
            
    ax = fig.add_subplot(1,1,1)
    fig.subplots_adjust(top=0.85)
    ax.set_xlabel('Project')
    ax.set_ylabel('Hours')
    
    for key in report_data.iterkeys():
        report_data[key] = report_data[key]/60
    
    pyplot.bar(range(len(report_data)), report_data.values(), align='center')
    pyplot.xticks(range(len(report_data)), list(report_data.keys()))
    
    pyplot.show()

def main():
    """Main method parses arguments and runs subroutines."""
    #first thing we do is load/init config
    load_config()

    #prepare argparser
    top_argparser = argparse.ArgumentParser(
        description="Track what you're doing")

    top_argparser.add_argument("action",
                               choices=["ls",
                                        "track",
                                        "report",
                                        "report_graph",
                                        "remove",
                                        "add"])

    top_args = top_argparser.parse_args(sys.argv[1:2])

    #each action has their own sub-args
    if top_args.action == "add":

        add_argparse = argparse.ArgumentParser(description="Add some time")
        add_argparse.add_argument("project",
                                  help="Name of project to track")
        add_argparse.add_argument("time",
                                  help="Time to budget or 'live' for \
                                  live timer")
        add_argparse.add_argument("comment", nargs="+",
                                  help="What did you do in this time")
        add_argparse.add_argument("-w", "--when", dest="when", default="now",
                                  help="When to insert time. \
                                  Defaults to today")

        args = add_argparse.parse_args(sys.argv[2:])
        add(args)

    if top_args.action == "report":
        rpt_argparse = argparse.ArgumentParser(description="Generate report")
        rpt_argparse.add_argument("-w", "--week", dest="week",
                                  action="store_true",
                                  help="List logs for this week")

        rpt_argparse.add_argument("-m", "--month", dest="month",
                                  action="store_true",
                                  help="List logs for this month")

        args = rpt_argparse.parse_args(sys.argv[2:])

        report(args)
        
    if top_args.action == "report_graph":
        rpt_argparse = argparse.ArgumentParser(description="Generate graphical report")
        rpt_argparse.add_argument("-w", "--week", dest="week",
                                  action="store_true",
                                  help="List logs for this week")

        rpt_argparse.add_argument("-m", "--month", dest="month",
                                  action="store_true",
                                  help="List logs for this month")

        args = rpt_argparse.parse_args(sys.argv[2:])

        report_graph(args)

    if top_args.action == "ls":
        ls_argparse = argparse.ArgumentParser(description="List time logs")
        ls_argparse.add_argument("-w", "--week", dest="week",
                                 action="store_true",
                                 help="List logs for this week")
        ls_argparse.add_argument("-m", "--month", dest="month",
                                  action="store_true",
                                  help="List logs for this month")

        args = ls_argparse.parse_args(sys.argv[2:])

        list_logs(args)

    if top_args.action == "remove":

        rm_argparse = argparse.ArgumentParser(description="Remove log entry")
        rm_argparse.add_argument("line", help="Entry to remove")

        args = rm_argparse.parse_args(sys.argv[2:])
        delete(args)


if __name__ == "__main__":
    main()
