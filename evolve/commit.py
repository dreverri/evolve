from evolve.schema import Schema
import copy

class CommitNotFound(Exception):
    pass


class InvalidChange(Exception):
    pass


class Commit(object):
    def __init__(self, repository):
        self.repository = repository
        self.parent = None
        self.changelog = None
        self.schema = None
        self.commit_id = None
        self.msg = None
        self.checkedout = False
        
    def checkout(self, commit_id):
        if self.checkedout:
            return
        
        try:
            commit_dict = self.repository.commits[commit_id]
        except KeyError:
            raise CommitNotFound("Could not find the commit %s" % commit_id)
        
        self.commit_id = commit_id
        self.msg = commit_dict['msg']
        
        if 'parent' in commit_dict:
            self.parent = Commit(self.repository)
            self.parent.checkout(commit_dict['parent'])
            self.schema = copy.deepcopy(self.parent.schema)
        else:
            self.parent = None
            self.schema = Schema()
        
        self.changelog = commit_dict['changelog']
            
        for change in self.changelog:
            self.schema.add(change)
            
        self.checkedout = True
        
    def toDict(self):
        d = {
            'changelog':self.changelog,
            'msg':self.msg
        }
        
        if self.parent:
            d['parent'] = self.parent.commit_id
            
        return d    
    
    def getAncestors(self):
        if self.parent:
            parents = self.parent.getAncestors()
            parents.append(self.commit_id)
            return parents
        else:
            return [self.commit_id]
    
    def rollback(self, to_commit=None):
        """Returns a changelog that will rollback the current commit to the given commit_id.
        
        If to_commit is None than only this commit will be rolled back in the changelog."""
        if to_commit is self.commit_id:
            raise InvalidChange("Can't rollback to self")
            
        if not to_commit:
            to_commit = self.parent.commit_id
            
        ancestors = self.getAncestors()
        if to_commit not in ancestors:
            raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (to_commit, self.commit_id))
            
        revlog = [self.reverse(change) for change in self.changelog]
        revlog.reverse()
            
        if self.parent.commit_id is not to_commit:
            parentlog = self.parent.rollback(to_commit)
            revlog.extend(parentlog)
        
        return revlog
        
    def rollforward(self, from_commit=None):
        """Return changelog from given commit to current commit"""
        if from_commit is self.commit_id:
            raise InvalidChange("Can't rollback to self")
            
        if not from_commit:
            from_commit = self.parent.commit_id
            
        ancestors = self.getAncestors()
        if from_commit not in ancestors:
            raise CommitNotFound("Did not find %s in the list of ancestors of %s" % (from_commit, self.commit_id))

        log = copy.deepcopy(self.changelog)

        if self.parent.commit_id is not from_commit:
            parentlog = self.parent.rollforward(from_commit)
            parentlog.extend(log)
            log = parentlog

        return log
        
    def reverse(self, change):
        action = change['change']
        table = change['schema']['id']
        fields = change['schema']['properties']
        new_change = copy.deepcopy(change)
        if 'old_schema' in new_change:
            del new_change['old_schema']
        
        if action == 'create':
            new_change['change'] = 'drop'
            
        if action == 'drop':
            new_change['change'] = 'create'
            new_change['schema'] = change['old_schema']
            
        if action == 'alter.add':
            new_change['change'] = 'alter.drop'

        if action == 'alter.modify':
            for field in fields:
                old = change['old_schema']['properties'][field]
                new_change['schema']['properties'][field] = old
            
        if action == 'alter.rename':
            for field in fields:
                newname = fields[field]
                new_change['schema']['properties'][newname] = field
                del new_change['schema']['properties'][field]
            
        if action == 'alter.drop':
            new_change['change'] = 'alter.add'
            for field in fields:
                old = change['old_schema']['properties'][field]
                new_change['schema']['properties'][field] = old
                
        return new_change