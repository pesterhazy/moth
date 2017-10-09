#!/usr/bin/env python2

import errno
import os
import sys
import urllib2
import hashlib

MAIN_SHA = "SHA_GOES_HERE"


def get_main_sha():
    # careful because SHA_GOES_HERE is replaced
    if MAIN_SHA.startswith("SHA_GOES_"):
        return os.environ.get("MOTH_VERSION")
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
    if os.environ.get("MOTH_GLOBAL_CACHE"):
        return os.environ.get("MOTH_GLOBAL_CACHE")
    else:
        return os.path.expanduser("~/.cache/moth")


spinner_images = ["[    ]",
                  "[=   ]",
                  "[==  ]",
                  "[=== ]",
                  "[ ===]",
                  "[  ==]",
                  "[   =]",
                  "[    ]",
                  "[   =]",
                  "[  ==]",
                  "[ ===]",
                  "[====]",
                  "[=== ]",
                  "[==  ]",
                  "[=   ]"]


def echo(s):
    if sys.stderr.isatty():
        sys.stderr.write(s)
        sys.stderr.flush()


def download(url, sha, target_file):
    try:
        url_file = urllib2.urlopen(url)
    except urllib2.URLError as e:
        sys.stderr.write("\n")
        sys.stderr.write("Could not download: " + str(e) + "\n")
        sys.stderr.write("Url: " + url + "\n")

        sys.exit(1)

    hasher = hashlib.sha1()

    mkdir_p(os.path.dirname(target_file))

    with open(target_file, "w") as out:
        n_chunks = 0
        chunk_size = 1024 * 64
        image = spinner_images[len(spinner_images) - 1]
        echo(image)
        while 1:
            data = url_file.read(chunk_size)
            if not data:
                break
            hasher.update(data)
            out.write(data)
            echo("\b" * len(spinner_images[0]))
            echo(spinner_images[n_chunks % len(spinner_images)])
            n_chunks += 1

    echo("\b" * (len(spinner_images[0])) +
         " " * (len(spinner_images[0])) +
         "\b" * (len(spinner_images[0])))

    downloaded_sha = hasher.hexdigest()

    if downloaded_sha != sha:
        raise Exception("Downloaded sha " + downloaded_sha +
                        " does not match expected value " + sha)


def bootstrap(sha, target_file):
    if os.environ.get("MOTH_BOOTSTRAP_BASE") is not None:
        base_url = os.environ.get("MOTH_BOOTSTRAP_BASE")
    else:
        base_url = "https://github.com/pesterhazy/moth/releases/download/r"

    url = base_url + get_main_sha() + "/moth_release.zip"

    sys.stderr.write("moth: bootstrapping version " + sha + ": ")
    sys.stderr.flush()

    download(url, sha, target_file)

    sys.stderr.write("done.\n")


def get_zip_path(sha):
    return os.path.join(cache_base_path(), "binary", sha)


def start():
    main_sha = get_main_sha()
    ZIP_PATH = get_zip_path(main_sha)

    if os.path.exists(ZIP_PATH):
        sys.path.insert(0, ZIP_PATH)

    try:
        import moth.main
    except ImportError:
        bootstrap(main_sha, ZIP_PATH)

        if os.path.exists(ZIP_PATH):
            sys.path.insert(0, ZIP_PATH)

        import moth.main

    moth.main.run(os.path.dirname(__file__), main_sha)


start()
