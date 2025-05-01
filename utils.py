"""Utility functions for Tesla Connector integration."""


def get_value_from_path(data, path: str):
    """Get attribute from nested data based on a dot path."""
    for part in path.split("."):
        data = getattr(data, part, None)
        if data is None:
            break
    return data
