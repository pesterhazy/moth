import os.path
import yaml


def find_root(fn):
    prev, fn = None, os.path.abspath(fn)
    while prev != fn:
        if os.path.isfile(os.path.join(fn, "moth.yaml")):
            return fn
        prev, fn = fn, os.path.abspath(os.path.join(fn, os.pardir))
    raise Exception("No project root containing moth.yaml found")


def read_manifest(root_path):
    fname = os.path.join(root_path, "moth.yaml")

    with open(fname, 'r') as f:
        return yaml.load(f)
