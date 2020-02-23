import requests

from datetime import datetime
from timetrack import TTBaseDriver

USER_AGENT = "timetrack 1.0"
HARVEST_ENDPOINT = "https://api.harvestapp.com/v2"

class TTHarvestDriver(TTBaseDriver):
    

    
    def __init__(self, ACCESS_TOKEN, ACCOUNT_ID):
        """Create harvest driver"""
        self.access_token = ACCESS_TOKEN
        self.account_id = ACCOUNT_ID
        self._user_profile = None
        self._project_map = None
        
    def get_default_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Harvest-Account-Id": self.account_id,
            "User-Agent": USER_AGENT
        }
        
    @property
    def user_profile(self):
        if self._user_profile is None:
            self._user_profile = self.get_user_info()
            
        return self._user_profile
        
    def request(self, rqfunc, endpoint, additional_headers={}, *args, **kwargs):
        
        headers = self.get_default_headers()
        headers.update(additional_headers)
        
        r = rqfunc(f"{HARVEST_ENDPOINT}{endpoint}", headers=headers, *args, **kwargs)
        return r
        
    def get_user_info(self):
        
        r = self.request(requests.get, "/users/me")
        return r.json()
    
    def add_entry(self, project, time, comment, when=datetime.now(), task=None):
        projbits = project.split("/")
        
        if len(projbits) < 2: #expect ProjectCode or Projectcode/ProjectName
            project_id = projbits[0]
        else: #expect Client/ProjectCode/ProjectName
            project_id = projbits[1]
            
            
    
    def delete_entry(self, entry_id):
        pass
    
    def update_entry(self, entry_id, time):
        pass
    
    def get_project_map(self):
        if self._project_map is None:
            r = self.request(requests.get, f"/users/{self.user_profile['id']}/project_assignments")
        
            self._project_map = {p['project']['code']: p for p in r.json()['project_assignments']}
            
        return self._project_map
        
            
    def get_filtered_entries(self, start=None, finish=None, project=None):
        
        params = {
            "user": self.user_profile['id'],
            "from": start.strftime("%Y-%m-%d"),
            "to": finish.strftime("%Y-%m-%d")
        }
        
        #we need this later but we need it for filtering by project too
        project_map = self.get_project_map()
        
        if project is not None:
            
            if project not in project_map:
                raise Exception(f"Unknown project code {project}. Project not known.")
            
            params['project_id'] = project_map[project]['project']['id']
            
        r = self.request(requests.get, f"/time_entries", params=params)
        
        id2code = {p['project']['id']: p['project']['code'] for p in project_map.values()}
        
        entries = []
        for entry in r.json()['time_entries']:
            entry['date'] = entry['spent_date']
            entry['project'] = entry['client']['name'] + "/" + id2code[entry['project']['id']] + "/" + entry['project']['name']
            entry['time'] = entry['hours'] * 60
            entry['comment'] = entry.get('notes', "")
            yield entry
        
    def get_projects(self):
        """Return a list of projects that the authenticated user is allowed to see"""

        r = self.request(requests.get, f"/users/{self.user_profile['id']}/project_assignments")
        
        return sorted([p['client']['name'] + '/' + p['project']['code'] + "/" + p['project']['name'] 
                for p in r.json()['project_assignments'] if p['is_active']])
        
    def get_tasks(self, project=None):
        """Return list of tasks supported by harvest"""
        
        r = self.request(requests.get, f"/users/{self.user_profile['id']}/project_assignments")
        
        projects = [p for p in r.json()['project_assignments'] if p['is_active']]
        
        tasks = []
        
        for p in projects:
            if (project is None) or (p['project']['code'] == project):
                tasks.extend([t['task']['name'] for t in p['task_assignments'] if t['is_active']])
        
        return sorted(list(set(tasks)))