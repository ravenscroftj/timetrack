from setuptools import setup, find_packages

setup(
    name = "timetrack",
    version = 0.1,
    packages = find_packages(),

    #install requirements
    install_requires = ['progressbar2'],

    entry_points = {"console_scripts" : [
        'timetrack = timetrack.timetrack:main',
        ]},

    author="James Ravenscroft",
    author_email = "ravenscroft@gmail.com",
    description = "Simple command line tool for managing your time",
    url="http://www.brainsteam.co.uk/"

)
