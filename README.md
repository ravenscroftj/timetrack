# timetrack - a simple commandline time tracking tool

timetrack is a simple tool for monitoring how much time you are spending on
different projects. It is inspired by [Harvest](https://www.getharvest.com/),
[RescueTime](https://www.rescuetime.com/) and their ilk but is much simpler and
100% completely free to use for ever.


## Installation

To install timetrack simply run

````
    python setup.py install  
````

The module will be installed and timetrack should be available on your system
path.


## Configuration

timetrack loads its configuration from a file in your user directory called
~/.timetrack. Here you can define the following:

  * track_file: path to the actual file you want to use to log to.
  * working_hours: number of hours you work per day - used to calculate remaining
     time in the list command

## Usage

timetrack will store its logs in your user directory at ~/.timetrack.

### Adding time to the logger

#### Add time to a project you've worked on today

You can add time to a project by running

````
timetrack  add <project_name> 1h30m "some comment on what you did."
````

Project names can be arbitrary and are not validated. Every time you run `add`
with the same project name, this information can be used to tally up your total
time spent on that project using the report command (explained below). Project
names are case sensitive.

timetrack uses XhYm to report that you spent X hours and Y minutes on a project.

timetrack will assume that any arguments after the time argument are part of
the comment which means you don't have to put quotes around it. For example

````
timetrack  add <project_name> 1h30m look ma, no quotes!
````

#### Using the live timer to add time to something you are working on now

The easiest way to keep on top of what you're working on is to use Timetrack's
live logger. simply replace the time argument in the add command with "live"
like in the following example

    timetrack  add spam_eating live "ate spam for my lunch"

You will find that timetrack goes into live timer mode

````
Starting timer, press Ctrl + C at any time to end recording...
Project:spam_eating Elapsed Time: 0:15:29
````

When you have finished working on the project you can press CTRL+C on your
keyboard to record your timings. timetrack will round down to the nearest
minute and will refuse to log your time if you have been working for less than
1 minute.

#### Logging stuff you did in the past

If you suddenly remember you did some work on a project last week you can add
time in hindsight by using the `-w` argument with add - like so:

````
timetrack.py add PhD 3h -w 2016-11-22 did some stuff on my thesis.
````

The date format is YYYY-MM-DD. timetrack will error if you try and use any other
date format.


### Viewing what you've done today/this week/this month

To see what you've logged so far  you can use the `timetrack ls` command. By
default this will show you all the work you've logged so far today and guess at
how many hours you have left of useful time.

An example output can be seen here:

````
$ timetrack ls

2016-11-23
---------
1) 1h30m on timetrack: initial write of timetrack to keep track of stuff I do
2) 1h0m on PhD: swatting up on cluster queue systems
3) 0h15m on PhD: raise bug on cluster system
5) 1h0m on timetrack: implemented inserting old dates and listing your week
6) 0h34m on timetrack: working on timetrack
-----------
Remaining time today: 5h41m

````

If you want to see your timetrack log for the previous week or even month then
you can call `timetrack ls -w` or `timetrack ls -m` respectively.


### Per-project report

This view allows you to see how much time you have spent on each project. You
can see this summary for the current week or month by using `-w` or `-m` flags
respectively.

An example call and output can be seen below:

````
$ timetrack report -w  

Project Breakdown: 2016-11-16 to 2016-11-23
----------
PhD: 4h15m
timetrack: 3h4m
spam_eating: 1h15m
````

### Graphical per-project report

This view is much like above, but outputs a MatPlotLib bar or pie chart of the time spent
on each project. You can see this summary for the current week or month by using `-w` or
`-m` flags respectively, and can see a pie chart instead of the default bar graph with the
`-p` flag.

### Updating existing records

If you have recorded some time for a project, had to walk away and want to go
back to it (rather than create a new separate record), you can simply append
more time to it.You will notice that in the `timetrack ls` output each log
has a number next to it. This is the unique id of that entry. To add more time
to an entry simply run

````
timetrack append <id> <time>
````
Where id is the unique id of the entry and time is the amount of time to be
added. `live` is also accepted in append so you can continue to live time your
work.

### Removing erroneous records

If you have recorded some time that was incorrect, it is simple enough to remove.
You will notice that in the `timetrack ls` output each log has a number next to
it. This is the unique id of that entry. To remove a log entry simply run

````
timetrack remove <id>
````

The entry will be wiped from the system and the current day's logs will be shown
on screen.

NB: you can use `timetrack rm` as an alias for remove (to save keystrokes).

## License
This project is under the MIT open source license. Please see the LICENSE file
for the specifics.

## Contributing

If you would like to contribute to this project, simply clone it, make your
adjustments and raise a merge request.
