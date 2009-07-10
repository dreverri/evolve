import unittest
import os
import os.path
import shutil
import simplejson as json


class RepositoryAlreadyExists(Exception):
    pass


class FileRepository:
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
        

class FileRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.setup_new_directory()
        self.setup_existing_directory()
        self.setup_existing_repository()
        
    def tearDown(self):
        self.tear_down_new_directory()
        self.tear_down_existing_directory()
        self.tear_down_existing_repository()
        
    def setup_new_directory(self):
        self.new_directory = 'test_new_directory'
        if os.path.exists(self.new_directory):
            shutil.rmtree(self.new_directory)
            
    def tear_down_new_directory(self):
        if os.path.exists(self.new_directory):
            shutil.rmtree(self.new_directory)
            
    def setup_existing_directory(self):
        self.existing_directory = 'test_existing_directory'
        if os.path.exists(self.existing_directory):
            shutil.rmtree(self.existing_directory)
        os.mkdir(self.existing_directory)
        
    def tear_down_existing_directory(self):
        if os.path.exists(self.existing_directory):
            shutil.rmtree(self.existing_directory)
            
    def setup_existing_repository(self):
        self.existing_repository = 'test_existing_repository'
        repo = FileRepository()
        repo.initialize(self.existing_repository)
        
    def tear_down_existing_repository(self):
        if os.path.exists(self.existing_repository):
            shutil.rmtree(self.existing_repository)

    def assertRepo(self, repo_dir):
        repo_file = '%s/evolve.json' % repo_dir
        changes_file = '%s/changes.json' % repo_dir
        self.assertRepoDir(repo_dir)
        self.assertRepoFile(repo_file)
        self.assertRepoChangesFile(changes_file)

    def assertRepoDir(self, repo_dir):
        self.assertTrue(os.path.exists(repo_dir))

    def assertRepoFile(self, repo_file):
        self.assertTrue(os.path.exists(repo_file))
        f = open(repo_file, 'r')
        repo_data = json.load(f)
        for element in ['config', 'commits', 'changes', 'branches']:
            self.assertTrue(element in repo_data)
            self.assertTrue(type(repo_data[element]) is dict)

    def assertRepoChangesFile(self, changes_file):
        self.assertTrue(os.path.exists(changes_file))
        f = open(changes_file, 'r')
        changes_data = json.load(f)
        self.assertTrue('changes' in changes_data)
        self.assertTrue(type(changes_data['changes']) is list)
        
        
class FileRepositoryTest(FileRepositoryTestCase): 
    def test_initialize_new_directory(self):
        """Testing that evolve initializes a repository in a directory that 
        does not exist."""
        repo = FileRepository()
        repo.initialize(self.new_directory)
        self.assertRepoDir(self.new_directory)

    def test_initialize_existing_directory(self):
        """Testing that evolve initializes a repository in an existing 
        directory."""
        repo = FileRepository()
        repo.initialize(self.existing_directory)
        self.assertRepo(self.existing_directory)
        
    def test_initialize_existing_repo_failure(self):
        """Testing that evolve fails when trying to initialize an existing 
        repo."""
        try:
            repo = FileRepository()
            repo.initialize(self.existing_repository)
            self.fail("Expected RepositoryAlreadyExists exception")
        except RepositoryAlreadyExists, e:
            pass
        
        
if __name__ == '__main__':
    unittest.main()