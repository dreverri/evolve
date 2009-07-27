import unittest
from evolve.repository import *
from evolve.tests import reversible_changes


class EvolveRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        
    def commit_person_to_master_branch(self):
        self.repo.branch('master')
        changes = [
            {
                "change":"create",
                "schema":{
                    "id":"person",
                    "type":"object",
                    "properties":{
                        "id":{"type":"string"}
                    }
                }
            }
        ]
        self.repo.commit('master', changes, 'create person')
        
    def setup_repo_with_two_branches(self):
        self.commit_person_to_master_branch()
        b1 = self.repo.branch('b1','master')
        changes = [{
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "name":{"type":"string"}
                }
            }
        }]
        self.repo.commit('b1', changes, 'added name field')
        
        b2 = self.repo.branch('b2','master')
        changes2 = [{
            "change":"alter.add",
            "schema":{
                "id":"person",
                "type":"object",
                "properties":{
                    "last_name":{"type":"string"}
                }
            }
        }]
        self.repo.commit('b2', changes2, 'added last name field')
        
        
class TestEvolveRepositoryBranch(EvolveRepositoryTestCase):
    def test_branch(self):
        """Test that the repository creates a new branch"""
        commit = self.repo.branch('master')
        self.assertTrue(commit.commit_id in self.repo.commits.keys())
        
    def test_branch_from_parent_branch(self):
        """Test that the repository branches from a parent branch"""
        master = self.repo.branch('master')
        branch = self.repo.branch('branch', 'master')
        self.assertEqual(master.commit_id, branch.commit_id)
        
    def test_branch_existing_branch(self):
        self.repo.branch('master')
        try:
            self.repo.branch('master')
            self.fail('Expected branch() to raise BranchAlreadyExists')
        except BranchAlreadyExists:
            pass
            
    def test_branch_from_non_existing_parent(self):
        try:
            self.repo.branch('master', 'does_not_exist')
            self.fail('Expected branch() to raise BranchNotFound')
        except BranchNotFound:
            pass
        
        
class TestEvolveRepositoryCheckout(EvolveRepositoryTestCase):
    def test_checkout_branch(self):
        master = self.repo.branch('master')
        master1 = self.repo.checkout_branch('master')
        self.assertEqual(master.commit_id, master1.commit_id)
        
    def test_checkout_non_existing_branch(self):
        try:
            self.repo.checkout_branch('does_not_exist')
            self.fail('Expected checkout_branch() to raise BranchNotFound')
        except BranchNotFound:
            pass
            
    def test_checkout_commit_root_changelog(self):
        root = self.repo.checkout_commit('root')
        self.assertEqual(root.changelog, [])

    def test_checkout_commit_not_found(self):
        try:
            self.repo.checkout_commit('does_not_exist')
            self.fail("Expected checkout_commit to raise CommitNotFound")
        except CommitNotFound:
            pass

    def test_checkout_commit_with_parent(self):
        self.commit_person_to_master_branch()
        master = self.repo.checkout_branch('master')
        master1 = self.repo.checkout_commit(master.commit_id)
        self.assertEqual(master1.parent.commit_id, 'root')
        
    def test_checkout_commit_root_msg(self):
        root = self.repo.checkout_commit('root')
        self.assertEqual(root.msg, 'root')
        
        
class TestEvolveRepositoryCommit(EvolveRepositoryTestCase):
    def test_commit_schema_tables(self):
        self.commit_person_to_master_branch()
        master = self.repo.checkout_branch('master')
        self.assertTrue('person' in master.schema.tables.keys())
        
    def test_commit_schema_person_id(self):
        self.commit_person_to_master_branch()
        master = self.repo.checkout_branch('master')
        person_props = master.schema.tables['person']['properties'].keys()
        self.assertTrue('id' in person_props)
        
    def test_commit_msg(self):
        self.commit_person_to_master_branch()
        master = self.repo.checkout_branch('master')
        self.assertEqual(master.msg, 'create person')
    
    
class TestEvolveRepositoryRevChange(EvolveRepositoryTestCase):
    def compare_rev_changes(self, change, rev_change):
        rev_change1 = self.repo.rev_change(change)
        self.assertEqual(rev_change1, rev_change)
        
    def test_rev_change_create(self):
        change = reversible_changes.create
        rev_change = reversible_changes.drop
        self.compare_rev_changes(change, rev_change)
        
    def test_rev_change_drop(self):
        change = reversible_changes.drop
        rev_change = reversible_changes.create
        self.compare_rev_changes(change, rev_change)
    
    def test_rev_change_alter_add(self):
        change = reversible_changes.alter_add
        rev_change = reversible_changes.alter_drop
        self.compare_rev_changes(change, rev_change)
        
    def test_rev_change_alter_drop(self):
        change = reversible_changes.alter_drop
        rev_change = reversible_changes.alter_add
        self.compare_rev_changes(change, rev_change)

    def test_rev_change_alter_modify(self):
        change = reversible_changes.alter_modify
        rev_change = reversible_changes.alter_modify_reversed
        self.compare_rev_changes(change, rev_change)

    def test_rev_change_alter_rename(self):
        change = reversible_changes.alter_rename
        rev_change = reversible_changes.alter_rename_reversed
        self.compare_rev_changes(change, rev_change)

class TestEvolveRepositoryFindCommonParent(EvolveRepositoryTestCase):
    def test_find_common_parent(self):
        self.setup_repo_with_two_branches()
        b1 = self.repo.checkout_branch('b1')
        b2 = self.repo.checkout_branch('b2')
        master = self.repo.checkout_branch('master')
        parent_id = self.repo.find_common_parent(b1.commit_id, b2.commit_id)
        self.assertEqual(parent_id, master.commit_id)


class TestEvolveRepositoryRollback(EvolveRepositoryTestCase):
    def test_rollback(self):
        self.setup_repo_with_two_branches()
        b1 = self.repo.checkout_branch('b1')
        master = self.repo.checkout_branch('master')
        log = self.repo.rollback(b1.commit_id, master.commit_id)
        self.assertTrue(len(log) == 1)
        self.assertTrue(log[0]['change'] == 'alter.drop')
        self.assertTrue('name' in log[0]['schema']['properties'].keys())

class TestEvolveRepositoryRollforward(EvolveRepositoryTestCase):
    def test_rollforward(self):
        self.setup_repo_with_two_branches()
        b1 = self.repo.checkout_branch('b1')
        master = self.repo.checkout_branch('master')
        log = self.repo.rollforward(master.commit_id, b1.commit_id)
        self.assertTrue(len(log) == 1)
        self.assertTrue(log[0]['change'] == 'alter.add')
        self.assertTrue('name' in log[0]['schema']['properties'].keys())


class TestEvolveRepositoryMigrate(EvolveRepositoryTestCase):
    def test_migrate(self):
        self.setup_repo_with_two_branches()
        b1 = self.repo.checkout_branch('b1')
        b2 = self.repo.checkout_branch('b2')
        migration = self.repo.migrate(b1.commit_id,b2.commit_id)
        self.assertTrue(migration[0]['change'] == 'alter.drop')
        self.assertTrue('name' in migration[0]['schema']['properties'])
        self.assertTrue(migration[1]['change'] == 'alter.add')
        self.assertTrue('last_name' in migration[1]['schema']['properties'])
        
        
if __name__ == '__main__':
    unittest.main()