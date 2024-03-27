import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(SCRIPT_DIR, "config.json")) as f:
    conf = json.load(f)


def gc(arg, fail=False):
    if isinstance(arg, str):
        return conf.get(arg, fail)
    if isinstance(arg, list):
        if len(arg) == 1:
            return conf.get(arg, fail)
        else:  # len 2
            group = conf.get(arg[0])
            if not group:
                return fail
            return group[1]
