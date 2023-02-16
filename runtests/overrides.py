import json
"""
Provide a key/value means of speciying values.

Other modules must use override.get("key") to look for values.
"""
overrides = {}

def get(key, default=None):
    """
    If key exists in overrides, return the value.

    Otherwise, return defalt
    """
    global overrides

    if key in overrides:
        return overrides[key]

    return default

def set(key, value):
    """
    Set overrides key to the value
    """
    global overrides

    overrides[key] = value

def set_from_file(file_name):
    """
    Set overrides to the contents of the file.
    """
    global overrides

    data = {}
    with open(file_name, "r") as file:
        data = json.loads(file.read())
        file.close()

    overrides = data
