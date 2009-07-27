from evolve.exceptions import RepositoryAlreadyExists
import os

try:
    import json
except ImportError:
    import simplejson as json


class FileRepository(object):
    def initialize(self, directory):
        """Initialize the given directory"""
        if self.is_repository(directory):
            raise RepositoryAlreadyExists()
            
        if not os.path.exists(directory):
            os.mkdir(directory)
            
        self.initialize_repository_file(directory)    
        self.initialize_changes_file(directory)
        
    def is_repository(self, directory):
        repo_file = '%s/evolve.json' % directory
        return os.path.exists(repo_file)
        
    def initialize_repository_file(self, directory):
        repo_data = {
            "config": {},
            "commits": {},
            "changes": {},
            "branches": {}
        }
        repo_file = '%s/evolve.json' % directory
        self.write_to_file(repo_data, repo_file)
        
    def initialize_changes_file(self, directory):
        changes_data = {
            "changes": []
        }
        changes_file = '%s/changes.json' % directory
        self.write_to_file(changes_data, changes_file)
        
    def write_to_file(self, data, filename):
        f = open(filename, 'w')
        json.dump(data, f, indent=4)