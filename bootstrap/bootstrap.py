#!/usr/bin/env python2

import errno
import os
import sys
import urllib2
import hashlib

MAIN_SHA = "SHA_GOES_HERE"


def get_main_sha():
    if MAIN_SHA == "SHA_GOES_HERE":
        return os.environ["MOTH_VERSION"]
    else:
        return MAIN_SHA


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def cache_base_path():
    return os.path.expanduser("~/.cache/moth")


def bootstrap(sha, target_file):
    if os.environ.get("MOTH_BOOTSTRAP_REPO") is not None:
        base_url = os.environ.get("MOTH_BOOTSTRAP_REPO")
        url = base_url + "/db/" + sha[0:3] + "/" + sha + "/contents"
    else:
        url = "https://github.com/pesterhazy/moth/releases/download/r" + \
            get_main_sha() + "/moth_release.zip"

    sys.stderr.write("*** " + target_file +
                     " not found.\n*** Attempting to bootstrap\n***\n")
    sys.stderr.write("*** Downloading: " + url + "...")

    sys.stderr.flush()

    contents = urllib2.urlopen(url).read()

    downloaded_sha = hashlib.sha1(contents).hexdigest()

    if downloaded_sha != sha:
        raise Exception("Downloaded sha " + downloaded_sha +
                        " does not match expected value " + sha)

    mkdir_p(os.path.dirname(target_file))

    with open(target_file, "w") as out:
        out.write(contents)

    sys.stderr.write(" done.\n***\n\n")


def get_zip_path(sha):
    return os.path.join(cache_base_path(), "binary", sha)


def start():
    ZIP_PATH = get_zip_path(get_main_sha())

    if os.path.exists(ZIP_PATH):
        sys.path.insert(0, ZIP_PATH)

    try:
        import moth.main
    except ImportError:
        bootstrap(get_main_sha(), ZIP_PATH)

        if os.path.exists(ZIP_PATH):
            sys.path.insert(0, ZIP_PATH)

        import moth.main

    moth.main.run(os.path.dirname(__file__))


start()
