from datetime import datetime

from timetrack import TTBaseDriver
from typing import Optional
from configparser import ConfigParser

class TTRouterException(Exception):
    """Exceptions thrown by timetrack router"""

class TTRouterDriver(TTBaseDriver):
    """This ttrouter allows you to mix and match multiple drivers"""
    
    def __init__(self, config: ConfigParser, rootsection: Optional[str] = "router"):
        
        
        self.drivers = {}
        
        drivernames = config.get(rootsection, "drivers", fallback="").split(",")
        
        if len(drivernames) < 1:
            raise  TTRouterException("You must specify at least 1 router subdriver")
        
        for driver in drivernames:
            # get driver config
            dtype = config.get(driver, "driver")
            prefix = config.get(driver, "prefix")
            
            if dtype == "harvest":
                from timetrack.harvest import TTHarvestDriver
                
                dr = TTHarvestDriver(config, rootsection=driver)
                
            elif dtype == "file":
                from timetrack import TTFileDriver
                
                dr = TTFileDriver(config, rootsection=driver)
                
            self.drivers[prefix] = dr
            
    def add_entry(self, project, time, comment, when=datetime.now(), task=None):
        
        pre, project_name = project.split("_", maxsplit=1)
        
        if pre not in self.drivers:
            raise TTRouterException(f"Unknown driver prefix {pre}")
        
        driver = self.drivers[pre]
        
        pre, taskname = task.split("_", maxsplit=1)
        
        if pre not in self.drivers:
            raise TTRouterException(f"Unknown driver prefix {pre}")
        
        return driver.add_entry(project_name, time, comment, when, taskname)
    
    def get_filtered_entries(self, start=None, finish=None, project=None):
        
        entries = []
        
        for prefix, dr in self.drivers.items():
            dr_entries = dr.get_filtered_entries(start, finish, project)
            
            for entry in dr_entries:
                entry['id'] = prefix + "_" + str(entry['id'])
                entry['project'] = prefix + "_" + str(entry['project'])
                
                entries.append(entry)
                
        return entries
    
    def get_projects(self):
        """Return a list of projects that the authenticated user is allowed to see"""

        projects = []
        
        for prefix, dr in self.drivers.items():
            projects.extend([f"{prefix}_{p}" for p in dr.get_projects()])
            
        return projects
    
    def delete_entry(self, entry_id):
        return super().delete_entry(entry_id)
    
    def get_tasks(self, project=None):
        
        tasks = []
        
        for prefix, dr in self.drivers.items():
            tasks.extend([f"{prefix}_{t}" for t in dr.get_tasks()])
            
        return tasks
    
    def update_entry(self, entry_id, time):
        return super().update_entry(entry_id, time)