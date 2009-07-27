create = {
    "change":"create",
    "schema":{
        "id":"person",
        "type":"object",
        "properties":{
            "id":{"type":"string"}
        }
    }
}

drop = {
    "change":"drop",
    "schema":{
        "id":"person",
        "type":"object",
        "properties":{
            "id":{"type":"string"}
        }
    }
}

alter_add = {
    "change": "alter.add",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "name": {"type":"string"}
        }
    }
}

alter_drop = {
    "change": "alter.drop",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "name": {"type":"string"}
        }
    }
}

alter_modify = {
    "change": "alter.modify",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "id": {"type":"string", "maxLength":40}
        }
    },
    "old_schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "id": {"type":"string"}
        }
    }
}

alter_modify_reversed = {
    "change": "alter.modify",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "id": {"type":"string"}
        }
    },
    "old_schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "id": {"type":"string", "maxLength":40}
        }
    }
}

alter_rename = {
    "change": "alter.rename",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "id": "new_id"
        }
    }
}

alter_rename_reversed = {
    "change": "alter.rename",
    "schema": {
        "id": "person",
        "type": "object",
        "properties": {
            "new_id": "id"
        }
    }
}