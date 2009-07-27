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
        "type":"object"
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
            "name": {}
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