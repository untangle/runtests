"""
Overrides that modules can import
"""
overrides = {}

def get(key):
    """
    If key exists in overrides, return
    """
    global overrides

    if key in overrides:
        return overrides[key]

    return None

def set(new_overrides):
    global overrides

    overrides = new_overrides
