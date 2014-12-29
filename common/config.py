import json
import glob
import logging
import os

config = {}

log = logging.getLogger(__name__)

def get(key, default_value=None):
    path = key.split(".")
    value = config.copy()
    for i in path:
        if i not in value:
            value = None
            break

        value = value[i]
    return value or default_value

def getint(key, default=None):
    r = get(key, default)
    if r:
        return int(r)
    return default

def getfloat(key, default=None):
    return float(get(key, default))

def deep_merge(d1, d2):
    res = d1
    for key, value in d2.iteritems():
        if key in d1:
            if isinstance(value, dict) and isinstance(d1[key], dict):
                d1[key] = deep_merge(d1[key], value)
                continue
        d1[key] = value
    return d1

def read_config(*folders):
    global config
    files = []
    if not folders:
        folders = ["conf.d/*.json"]

    for folder in folders:
        files.extend(glob.glob(folder))

    filtered = []
    [filtered.append(i) for i in files if not filtered.count(i)]
    files = filtered

    for f in files:
        with open(f, "r") as config_file:
            try:
                data = json.load(config_file)
            except ValueError, e:
                log.exception("Failed to read config file %s", f)
                continue

            config = deep_merge(config, data)

    return config
