from evolve.commit import Commit
import copy
import hashlib

try:
    import json
except ImportError:
    import simplejson as json


class Branch(object):
    def __init__(self, repository, name, parent):
        self.repository = repository
        self.name = name
        self.parent = parent
        self.reset()
        
    def verify(self,change):
        return self.schema.verify(change)

    def add(self, change):
        if self.verify(change):
            self.schema.add(change)
            self.changelog.append(change)
        else:
            raise InvalidChange

    def commit(self, msg):
        commit = Commit(self.repository)
        commit.parent = self.parent
        commit.changelog = self.changelog
        commit.schema = self.schema
        commit.msg = msg
        commit.commit_id = hashlib.sha1(json.dumps(commit.toDict())).hexdigest()
        commit.checkedout = True
        self.repository.commits[commit.commit_id] = commit.toDict()
        self.repository.checkouts[commit.commit_id] = commit
        self.repository.branches[self.name] = commit.commit_id
        self.parent = commit
        self.reset()
        
    def reset(self):
        self.schema = copy.deepcopy(self.parent.schema)
        self.changelog = []