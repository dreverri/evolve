import unittest
from evolve.repository import *
from evolve.commit import *


class TestEvolveCommit(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('master')
        branch.add(change)
        branch.commit('test commit')
        
    def test_getAncestors(self):
        branch = self.repo.checkout('master')
        commit = branch.parent
        a = commit.getAncestors()
        self.assertTrue('root' in a)
        self.assertTrue(branch.parent.commit_id in a)
        
    def test_rollback(self):
        branch = self.repo.checkout('master')
        commit = branch.parent
        revlog = commit.rollback('root')
        self.assertEqual(len(revlog),1)
        self.assertTrue(revlog[0]['change'] == 'drop')
        
    def test_reverse_create(self):
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.checkout('master')
        commit = branch.parent
        reverse_change = commit.reverse(change)
        self.assertTrue(reverse_change['change'] == 'drop')
        
    def test_reverse_drop(self):
        change = {
            "change":"create",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "id":{"type":"string"}
                }
            }
        }
        branch = self.repo.branch('reverse_drop','master')
        commit = branch.parent
        change1 = commit.reverse(change)
        branch.add(change1)
        branch.commit('drop table')
        commit = branch.parent
        change2 = commit.reverse(change1)
        self.assertTrue(change2['change'] == 'create')
        
    def test_reverse_alter_add(self):
        branch = self.repo.branch('reverse_alter_add','master')
        change = {
            'change':'alter.add',
            'schema':{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string"}
                }
            }
        }
        branch.add(change)
        branch.commit('reverse_alter_add')
        commit = branch.parent
        c2 = commit.reverse(change)
        self.assertTrue(c2['change'] == 'alter.drop')
    
    def test_reverse_alter_modify(self):
        branch = self.repo.branch('reverse_alter_modify','master')
        c1 = {
            'change':'alter.add',
            'schema':{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string"}
                }
            }
        }
        c2 = {
            'change':'alter.modify',
            'schema':{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string","maxLength":50}
                }
            }
        }
        branch.add(c1)
        branch.add(c2)
        branch.commit('reverse_alter_modify')
        commit = branch.parent
        c3 = commit.reverse(c2)
        self.assertTrue(c3['change'] == 'alter.modify')
        self.assertFalse('maxLength' in c3['schema']['properties']['name'])


if __name__ == '__main__':
    unittest.main()