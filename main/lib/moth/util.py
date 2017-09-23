import os.path

def find_root(fn):
  prev, fn = None, os.path.abspath(fn)
  while prev != fn:
    if os.path.isfile(os.path.join(fn, "moth.yaml")):
      return fn
    prev, fn = fn, os.path.abspath(os.path.join(fn, os.pardir))
  raise Exception("No project root containing moth.yaml found")
