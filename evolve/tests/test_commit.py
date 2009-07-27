import unittest
from evolve.repository import *
from evolve.commit import *


class TestEvolveCommit(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        changes = [{
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }]
        branch = self.repo.branch('master')
        self.repo.commit('master', changes, 'create person')
        
    def test_get_ancestors(self):
        commit = self.repo.checkout_branch('master')
        a = commit.get_ancestors()
        self.assertTrue('root' in a)
        self.assertTrue(commit.commit_id in a)
        
    def test_to_dict_msg(self):
        commit = self.repo.checkout_branch('master')
        commit_dict = commit.to_dict()
        self.assertEqual(commit_dict['msg'], 'create person')
        
    def test_to_dict_changelog(self):
        commit = self.repo.checkout_branch('master')
        commit_dict = commit.to_dict()
        self.assertEqual(type(commit_dict['changelog']), list)
        
    def test_to_dict_parent(self):
        commit = self.repo.checkout_branch('master')
        commit_dict = commit.to_dict()
        self.assertEqual(commit_dict['parent'], 'root')
        
if __name__ == '__main__':
    unittest.main()