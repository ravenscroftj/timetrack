from setuptools import setup, find_packages

setup(
    name = "timetrack",
    version = "1.0a",
    packages = find_packages(),

    #install requirements
    install_requires = ['progressbar2',
                        'matplotlib',
                        'Click'],
    include_package_data=True,
    
    entry_points = {"console_scripts" : [
        'timetrack = timetrack.cli:cli',
        ]},

    author="James Ravenscroft",
    author_email = "ravenscroft@gmail.com",
    description = "Simple command line tool for managing your time",
    url="http://www.brainsteam.co.uk/"

)
