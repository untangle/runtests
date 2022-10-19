"""
Provide a key/value means of speciying values.

Other modules must use override.get("key") to look for values.
"""
overrides = {}

def get(key):
    """
    If key exists in overrides, return the value.

    Otherwise, return None
    """
    global overrides

    if key in overrides:
        return overrides[key]

    return None

def set(new_overrides):
    """
    Set the entire override structure hash.
    """
    global overrides

    overrides = new_overrides
