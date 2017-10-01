import os.path
import json
import hashlib


class UsageException(Exception):
    pass


def find_root(fn):
    prev, fn = None, os.path.abspath(fn)
    while prev != fn:
        if os.path.isfile(os.path.join(fn, "moth.json")):
            return fn
        prev, fn = fn, os.path.abspath(os.path.join(fn, os.pardir))
    return os.path.abspath(".")


def read_manifest(root_path):
    fname = os.path.join(root_path, "moth.json")

    with open(fname, 'r') as f:
        return json.load(f)


def write_manifest(data, root_path):
    fname = os.path.join(root_path, "moth.json")

    with open(fname, 'w') as out:
        json.dump(data, out, indent=4, separators=(',', ': '))


def pjoin(*args):
    return "/".join(args)


def hash_file(fn):
    return hashlib.sha1(file(fn).read()).hexdigest()
