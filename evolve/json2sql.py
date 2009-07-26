from sqlalchemy import *
from migrate import *


class JSONSchemaTypeToSQLColumnType(object):
    allowed_types = [
        "string", 
        "number", 
        "integer", 
        "boolean", 
        "object", 
        "array"
        ]
    
    def __init__(self, prop=None):
        self.prop = prop
        
    def set_prop(self, prop):
        self.prop = prop
        
    def get_column_type(self):
        # prop must contain "type"
        _type = self.prop["type"]
        if _type not in self.allowed_types:
            raise ValueError
        if hasattr(self, _type):
            _type_func = getattr(self, _type)
            column_type = _type_func()
        else:
            raise NotImplementedError
        return column_type
            
    def string(self):
        if "format" in self.prop:
            return self.string_with_format()
        else:
            return self.string_without_format()
    
    def string_with_format(self):
        prop = self.prop
        if prop["format"] == "date":
            return self.string_with_format_date()
        else:
            # unrecognized format, ignore it
            return self.string_without_format()
            
    def string_with_format_date(self):
        pass
        
    def string_without_format(self):
        prop = self.prop
        if "maxLength" in prop and prop["maxLength"]:
            return Unicode(length = prop["maxLength"])
        else:
            return UnicodeText()