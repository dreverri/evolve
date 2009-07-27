from evolve.commit import Commit
from evolve.schema import Schema
from evolve.exceptions import BranchNotFound
from evolve.exceptions import BranchAlreadyExists
from evolve.exceptions import NoCommonParent
from evolve.exceptions import CommitNotFound
import copy
import hashlib

try:
    import json
except ImportError:
    import simplejson as json


class Repository(object):
    def __init__(self):
        self.commits = {'root': {'changelog': [], 'msg': 'root'}}
        self.branches = {}
        self.checkouts = {}
        self.changes = {}
        
    def branch(self, branch_name, parent_branch_name=None):
        """Create a new branch.
        
        Returns Commit().
        """
        if branch_name in self.branches:
            raise BranchAlreadyExists("The branch %s already exists, use checkout_branch() instead" % branch_name)
            
        if parent_branch_name:
            try:
                self.branches[branch_name] = self.branches[parent_branch_name]
            except KeyError:
                raise BranchNotFound("Could not find the %s branch" % parent_branch_name)
        else:
            self.branches[branch_name] = 'root'
        return self.checkout_branch(branch_name)
        
    def checkout_branch(self, branch_name):
        try:
            commit_id = self.branches[branch_name]
        except KeyError:
            raise BranchNotFound("Could not find the %s branch" % branch_name)
            
        return self.checkout_commit(commit_id)
        
    def checkout_commit(self, commit_id):
        commit = Commit()
        
        try:
            commit_dict = self.commits[commit_id]
        except KeyError:
            raise CommitNotFound("Could not find the commit %s" % commit_id)
        
        commit.commit_id = commit_id
        commit.msg = commit_dict['msg']
        commit.changelog = commit_dict['changelog']
        
        if 'parent' in commit_dict:
            commit.parent = self.checkout_commit(commit_dict['parent'])
            commit.schema = copy.deepcopy(commit.parent.schema)
        else:
            commit.parent = None
            commit.schema = Schema()
        
        for change_id in commit.changelog:
            change = self.changes[change_id]
            commit.schema.add(change)
        
        return commit
        
    def commit(self, branch_name, changes, msg):
        """Commit the given changes to the given branch_name"""
        old_commit = self.checkout_branch(branch_name)
        for change in changes:
            old_commit.schema.verify(change)
        
        new_commit = Commit()
        new_commit.msg = msg
        new_commit.parent = old_commit
        new_commit.schema = copy.deepcopy(old_commit.schema)
        for change in changes:
            change = new_commit.schema.make_change_reversible(change)
            change_id = hashlib.sha1(json.dumps(change)).hexdigest()
            self.changes[change_id] = change
            new_commit.schema.add(change)
            new_commit.changelog.append(change_id)
            
        new_commit_dict = new_commit.to_dict()
        new_commit_id = hashlib.sha1(json.dumps(new_commit_dict)).hexdigest()
        self.commits[new_commit_id] = new_commit_dict
        self.branches[branch_name] = new_commit_id
        
    def find_common_parent(self, commit_one, commit_two):
        """Find the common parent between the two commits if one exists"""
        one = self.checkout_commit(commit_one)
        two = self.checkout_commit(commit_two)
        listone = one.get_ancestors()
        listtwo = two.get_ancestors()
        def compare(a, b):
            common = None
            for index in range(len(a)):
                if a[index] is not b[index]:
                    return common
                common = a[index]
            return common
                
        if len(listone) < len(listtwo):
            common = compare(listone, listtwo)
        else:
            common = compare(listtwo, listone)
        
        if not common:
            raise NoCommonParent("The commits %s and %s do not share a common parent" % (commit_one, commit_two))
            
        return common
        
    def migrate(self, source, target):
        """Migrate from one commit to another"""
        parent = self.find_common_parent(source, target)
        source_log = self.rollback(source, parent)
        target_log = self.rollforward(parent, target)
        source_log.extend(target_log)
        return source_log
        
    def rollback(self, source, target):
        """Returns a list of changes that will rollback source to target."""
        if source == target:
            raise InvalidChange("Can't rollback to self")

        source_commit = self.checkout_commit(source)
        ancestors = source_commit.get_ancestors()
        if target not in ancestors:
            raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (target, source))

        revlog = [self.rev_change_id(ch) for ch in source_commit.changelog]
        revlog.reverse()

        if source_commit.parent.commit_id != target:
            parentlog = self.rollback(source_commit.parent.commit_id, target)
            revlog.extend(parentlog)

        return revlog

    def rollforward(self, source, target):
        """Return list of changes from source to target."""
        if source == target:
            raise InvalidChange("Can't rollforward to self")

        target_commit = self.checkout_commit(target)
        ancestors = target_commit.get_ancestors()
        if source not in ancestors:
            raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (source, target))

        log = [self.changes[ch] for ch in target_commit.changelog]
        
        parent_id = target_commit.parent.commit_id
        if parent_id != source:
            parentlog = self.rollforward(source, parent_id)
            parentlog.extend(log)
            log = parentlog
        
        return log
        
    def rev_change_id(self, change_id):
        change = self.changes[change_id]
        return self.rev_change(change)
        
    def rev_change(self, change):
        action = change['change']
        table = change['schema']['id']
        fields = change['schema']['properties']
        new_change = copy.deepcopy(change)

        if action == 'create':
            new_change['change'] = 'drop'

        if action == 'drop':
            new_change['change'] = 'create'

        if action == 'alter.add':
            new_change['change'] = 'alter.drop'
            
        if action == 'alter.drop':
            new_change['change'] = 'alter.add'

        if action == 'alter.modify':
            old = new_change['old_schema']
            new = new_change['schema']
            new_change['old_schema'] = new
            new_change['schema'] = old

        if action == 'alter.rename':
            for field in fields:
                newname = fields[field]
                new_change['schema']['properties'][newname] = field
                del new_change['schema']['properties'][field]

        return new_change