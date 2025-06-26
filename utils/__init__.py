import collections
import sys

is_mac = sys.platform.startswith("darwin")
is_win = sys.platform.startswith("win32")

# also covers *BSD
is_lin = not is_mac and not is_win


def dict_ignore_none(d):
    new_dict = collections.defaultdict(None)
    for key, value in d.items():
        if value is not None:
            new_dict[key] = value
    return new_dict


