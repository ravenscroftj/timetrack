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


## Usage

timetrack will store its logs in your user directory at ~/.timetrack.

### Adding time to the logger

#### Add time to a project you've worked on today

You can add time to a project by running

````
timetrack  add <project_name> 1h30m "some comment on what you did."
````

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
how many hours you have left of useful time
