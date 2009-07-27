import copy


class Schema(object):
    def __init__(self):
        self.tables = {}
        
    def verify(self, change):
        """Verify change against the working schema"""
        tables = self.tables
        action = change['change']
        schema = change['schema']
        table = schema['id']
        fields = schema['properties']
    
        if action == 'create':
            return table not in tables
        
        if action == 'drop':
            return table in tables
        
        if action == 'alter.add':
            if table not in tables:
                return False
            for field in fields:
                if field in tables[table]['properties']:
                    return False
            return True
        
        if action in ['alter.modify', 'alter.rename', 'alter.drop']:
            if table not in tables:
                return False
            for field in fields:
                if field not in tables[table]['properties']:
                    return False
            return True

    def add(self, change):
        """Add change to the working changelog, indexed per table, and working schema"""
        tables = self.tables
        action = change['change']
        schema = change['schema']
        table = change['schema']['id']
        fields = change['schema']['properties']

        if action == 'create':
            tables[table] = schema

        if action == 'drop':
            change['old_schema'] = copy.deepcopy(tables[table])
            del tables[table]

        if action == 'alter.add' or action == 'alter.modify':
            if action == 'alter.modify':
                change['old_schema'] = copy.deepcopy(tables[table])
            for field in fields:
                tables[table]['properties'][field] = fields[field]

        if action == 'alter.rename':
            for field in fields:
                newname = fields[field]
                tables[table]['properties'][newname] = tables[table]['properties'][field]
                del tables[table]['properties'][field]

        if action == 'alter.drop':
            change['old_schema'] = copy.deepcopy(tables[table])
            for field in fields:
                del tables[table]['properties'][field]
                
    def make_change_reversible(self, change):
        table = change['schema']['id']
        
        if change['change'] == 'drop':
            change['schema'] = self.tables[table]
            
        if change['change'] == 'alter.drop':
            for prop in change['schema']['properties']:
                change['schema']['properties'][prop] = self.tables[table]['properties'][prop]
                
        if change['change'] == 'alter.modify':
            change['old_schema'] = copy.deepcopy(change['schema'])
            for prop in change['old_schema']['properties']:
                change['old_schema']['properties'][prop] = self.tables[table]['properties'][prop]
                
        return change