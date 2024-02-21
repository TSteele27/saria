from functools import reduce
import re


def _get_value(default: any) -> callable:
    def iteree(current_value, path):
        if current_value is default:
            return current_value
        if current_value is None:
            return default
        if hasattr(current_value, path):
            return getattr(current_value, path)
        return current_value.get(path)

    return iteree


def _split_path(path: str) -> list[str]:
    pattern = r'\.(?=(?:[^"]*"[^"]*")*[^"]*$)'
    parts = re.split(pattern, s)
    parts = [part.strip('"') for part in parts]
    return parts


def get_path(path: str, from_value: dict, default: any = None) -> any:
    return reduce(_get_value(default), _split_path, from_value)
