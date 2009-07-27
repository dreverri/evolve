from evolve.schema import Schema
from evolve.exceptions import CommitNotFound
from evolve.exceptions import InvalidChange
import copy


class Commit(object):
    def __init__(self):
        self.parent = None
        self.changelog = []
        self.schema = None
        self.commit_id = None
        self.msg = None
        
    def to_dict(self):
        dct = {
            'changelog':self.changelog,
            'msg':self.msg
        }
        
        if self.parent:
            dct['parent'] = self.parent.commit_id
            
        return dct
    
    def get_ancestors(self):
        if self.parent:
            parents = self.parent.get_ancestors()
            parents.append(self.commit_id)
            return parents
        else:
            return [self.commit_id]