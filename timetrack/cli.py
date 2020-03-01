import click
import time
import traceback
import moment
from datetime import datetime, date, timedelta
from collections import defaultdict
from timetrack import TTFileDriver, load_config, human_time, day_remainder, day_spent, parse_time
from progressbar import ProgressBar, Timer
from matplotlib import pyplot

def live_time(project):
    """Run a timer actively in the window"""
    start = datetime.now()

    print("Starting timer, press Ctrl + C at any time to end recording...")

    running = True

    widgets = ['Project:{} '.format(project), Timer(), '']

    with ProgressBar(widgets=widgets) as pbar:
        while(running):
            try:
                time.sleep(1)
                pbar.update(0)
            except KeyboardInterrupt:
                running = False

    end = datetime.now()

    diff = end - start

    return (int(diff.total_seconds()) / 60)


def report_generate(records, echo=True):
    """Generate a list of items that have been tracked for given timeframe. """
    day_records = defaultdict(lambda: [])

    for record in records:
        dt = datetime.strptime(record['date'], "%Y-%m-%d")
        record_date = date(dt.year, dt.month, dt.day)
        day_records[record_date].append(record)

    if echo:  # only print if echo is on
        for day in sorted(day_records):
            records = day_records[day]

            print("\n{}\n---------".format(day.strftime("%Y-%m-%d")))
            for record in records:
                print(f"{record['id']}) {human_time(record['time'])} on {record['project']}: {record['comment']} ")

    return day_records

def init_context_obj():
    obj = {}
    obj['CONFIG'] = load_config()
    if obj['CONFIG']['timetrack'].get('driver', 'file') == "harvest":
        from timetrack.harvest import TTHarvestDriver
        
        obj['DRIVER'] = TTHarvestDriver(obj['CONFIG'])
    elif obj['CONFIG']['timetrack'].get('driver', 'file') == "router":
        from timetrack.router import TTRouterDriver
        
        obj['DRIVER'] = TTRouterDriver(obj['CONFIG'])
    else:
        obj['DRIVER'] = TTFileDriver(obj['CONFIG'])
    return obj

@click.group()
@click.pass_context
def cli(ctx):
    if ctx.obj is None:
        ctx.obj = init_context_obj()
    
def autocomplete_projects(ctx, args, incomplete):
    """Use the default driver to return a list of projects"""
    
    if ctx.obj is None:
        ctx.obj = init_context_obj()
        
    driver = ctx.obj['DRIVER']
    
    projects = driver.get_projects()
    
    options = [p for p in projects if  (len(incomplete) < 1) or (incomplete in p) ]
    
    return [f'"{option}"' if " " in option else option for option in options]

def autocomplete_tasks(ctx, args, incomplete):
    
    if ctx.obj is None:
        ctx.obj = init_context_obj()
    
    driver = ctx.obj['DRIVER']
    
    tasks = driver.get_tasks()
    
    #return args
    options = [t for t in tasks if (len(incomplete) < 1) or (incomplete in t)]
    return [f'"{option}"' if " " in option else option for option in options]


@cli.command()
@click.pass_context
@click.argument("project", type=str, autocompletion=autocomplete_projects)
@click.argument("time", type=str)
@click.argument("comment", type=str, nargs=-1)
@click.option("-d", "--date")
@click.option("-t", "--task", type=str, default=None, autocompletion=autocomplete_tasks)
def add(ctx, project, time, comment, date, task):
    """Add a time entry to a given project"""
    driver = ctx.obj['DRIVER']

    if time == "live":
        time = live_time(project)
        
    comment = " ".join(comment)
    
    if date is None:
        when = datetime.now()
        
    else:
        when = moment.date(date).datetime

    print("Adding {} minutes to {} project".format(parse_time(time), project))
    try:
        driver.add_entry(project, time, comment, when=when, task=task)
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

def parse_time_args(args):
    """"Parse week or month args or uses today by default."""
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

@cli.command()
@click.pass_context
@click.argument("entry", type=str, autocompletion=autocomplete_projects)
@click.argument("time", type=str)
def append(ctx, entry, time):
    """Append an amount of time to timetrack log"""
    
    if time == "live":
        time = live_time(f"Continuing work on entry {entry}")
        
        print("Adding {} minutes to entry {}".format(parse_time(time), entry))
        
    driver = ctx.obj['DRIVER']
    
    driver.update_entry(entry, time)

@cli.command()
@click.pass_context
@click.option("-p", "--project", type=str, default=None)
@click.option("-w", "--week", is_flag=True)
@click.option("-m", "--month", is_flag=True)
def ls(ctx, project, week, month):
    """Show tasks recorded between a certain time period"""

    driver = ctx.obj['DRIVER']

    if week:
        end = datetime.now()
        delta = timedelta(days=7)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    elif month:
        end = datetime.now()
        delta = timedelta(days=30)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    else:
        start_date = date.today()
        end_date = date.today()


    records = list(driver.get_filtered_entries(start_date, end_date, project))

    report_generate(records)

    today_str = date.today().strftime('%Y-%m-%d')

    today = [r for r in records if r['date']==today_str ]

    print("-----------")

    print("Time spent today: {}".format(
        human_time(day_spent(today))))
    print("Remaining time today: {}".format(
        human_time(day_remainder(today, working_hours=ctx.obj['CONFIG']['timetrack']['working_hours']))))

@cli.command()
@click.pass_context
def ls_prj(ctx):
    """List existing projects"""
    driver = ctx.obj['DRIVER']
    
    for project in driver.get_projects():
        print(project)
        

@cli.command()
@click.pass_context
@click.option("-p", "--project", type=str, default=None)
def ls_tasks(ctx, project):
    """List task types"""
    driver = ctx.obj['DRIVER']
    
    for task in driver.get_tasks(project):
        print(task)

@cli.command()
@click.pass_context
@click.argument("entry_id")
def rm(ctx, entry_id):
    "Delete timer entry"
    driver = ctx.obj['DRIVER']

    found = driver.delete_entry(entry_id)

    if found:
        print("Deleted entry")
    else:
        print("Could not find entry")


@cli.command()
@click.pass_context
@click.option("-w", "--week", is_flag=True)
@click.option("-m", "--month", is_flag=True)
@click.option("-g", "--graph", is_flag=True)
@click.option("--graph-type", type=click.Choice(['bar','pie'], case_sensitive=False), default='bar')
def report(ctx, week, month, graph, graph_type):
    """Summarise total time spent per project instead of per day"""
    
    
    driver = ctx.obj['DRIVER']
    
    if week:
        end = datetime.now()
        delta = timedelta(days=7)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    elif month:
        end = datetime.now()
        delta = timedelta(days=30)
        start = end - delta
        start_date = date(start.year, start.month, start.day)
        end_date = date(end.year, end.month, end.day)
    else:
        start_date = date.today()
        end_date = date.today()

    projects = defaultdict(lambda: 0)
    
    for record in driver.get_filtered_entries(start_date, end_date, project=None):

        dt = datetime.strptime(record['date'], "%Y-%m-%d")
        record_date = date(dt.year, dt.month, dt.day)

        if record_date >= start_date and record_date <= end_date:
            projects[record['project']] += record['time']

    if not graph:
        print("\nProject Breakdown: {} to {} \n----------".format(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")))

        for project, spent in projects.items():
            print("{}: {}".format(project, human_time(spent)))
    else:
        fig = pyplot.figure()
        titleString = "Project Breakdown: {}".format(start_date.strftime("%Y-%m-%d"))

        if start_date != end_date:
            titleString+=" to {}".format(end_date.strftime("%Y-%m-%d"))

        fig.suptitle(titleString, fontsize=14, fontweight='bold')

        ax = fig.add_subplot(1,1,1)
        fig.subplots_adjust(top=0.85)
        num_reports = len(projects)

        my_colors = ['c','m','y','r', 'g', 'b']

        for key in projects.keys():
            projects[key] = projects[key]/60.0

        if graph_type == "pie":
            pyplot.axis('equal')
            pyplot.pie(projects.values(), labels=list(projects.keys()), autopct='%1.1f%%', colors=my_colors, startangle=90)
        else:
            ax.set_xlabel('Project')
            ax.set_ylabel('Hours')
            pyplot.barh(range(num_reports), projects.values(), align='center', color=my_colors)
            pyplot.yticks(range(num_reports), list(projects.keys()))

    pyplot.show()

    return projects



if __name__ == "__main__":
    cli()
    