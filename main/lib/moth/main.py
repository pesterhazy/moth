import os
import sys
import re
import shutil
import zipfile
import tempfile
import json
from os.path import join
from optparse import OptionParser
import moth.version
import util
from util import UsageException
import fs

import s3
import file_provider


def croak():
    print '\xe2\x9b\x94\xef\xb8\x8f'
    sys.exit(1)


def fail(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(1)


def make_provider(url):
    if url.startswith("file:"):
        return file_provider.FileProvider(url)
    elif url.startswith("s3:"):
        return s3.S3Provider(url)

    raise Exception("No match for URL type: " + url)


def put(options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")
    if not repository:
        raise UsageException("No repository given")
    assert options.input_file

    provider = make_provider(repository)

    sha = provider.put(options.input_file)
    print sha


def get(options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")
    if not repository:
        raise UsageException("No repository given")
    assert options.sha, "Need to pass a sha"

    provider = make_provider(repository)
    provider.get(options.sha, options.output_file or "/dev/stdout")


def to_db_path(root_path):
    return join(root_path, ".moth", "db")


def to_tmp_path(root_path):
    return join(root_path, ".moth", "tmp")


def copy(from_fn, to_fn):
    shutil.copy(from_fn, to_fn)


def resolve_alias(root_path, alias):
    manifest = util.read_manifest(root_path)
    sha = manifest.get("aliases", {}).get(alias, {}).get("sha")
    assert sha, "Unable to resolve alias"
    return sha


def cat_or_print(fn, cat):
    if cat:
        shutil.copyfileobj(file(fn, "rb"), sys.stdout)
    else:
        print fn


def ensure(sha, repository, target_path):
    if not repository:
        raise UsageException("No repository given")

    content_path = join(target_path, "contents")

    if not os.path.isfile(target_path):
        provider = make_provider(repository)
        fs.mkdir_p(target_path)
        provider.get(sha, content_path)


def show(root_path, options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")

    sha = resolve_alias(
        root_path, options.alias) if options.alias else options.sha
    assert sha, "You need to specify a sha"

    target_path = join(to_db_path(root_path), sha[0:3], sha)
    content_path = join(target_path, "contents")

    ensure(sha, repository, target_path)

    if options.workspace or options.find:
        workspace_path = join(target_path, "workspace")

        if os.path.isfile(workspace_path):
            assert os.path.isdir(workspace_path)
        else:
            tmp_path = to_tmp_path(root_path)
            fs.mkdir_p(tmp_path)

            tmp_workspace_path = tempfile.mkdtemp(dir=tmp_path)
            try:
                zip_ref = zipfile.ZipFile(content_path, 'r')
                zip_ref.extractall(tmp_workspace_path)
                zip_ref.close()
                shutil.move(tmp_workspace_path, workspace_path)
                tmp_workspace_path = None
            finally:
                if tmp_workspace_path:
                    shutil.rmtree(tmp_workspace_path)

        if options.find:
            find_path = join(workspace_path, options.find)

            assert os.path.exists(
                find_path), "Specified file does not exist in workspace"
            cat_or_print(find_path, options.cat)
        else:
            print workspace_path
    else:
        cat_or_print(content_path, options.cat)


def init(options):
    assert not os.path.exists("moth.json"), "File already exists: moth.json"

    if not options.repository:
        raise UsageException("No repository given")


    data = {"repositories": [{"url": options.repository}]}

    with open("moth.json", "w") as out:
        json.dump(data, out, indent=4, separators=(',', ': '))

    print "Initialized moth project in current directory"
    print
    print "Initial repository:", options.repository


def is_valid_sha(s):
    return bool(re.match("^[0-9a-f]{40}$", s))


def action_alias(root_path, options):
    sha = options.sha
    assert options.alias
    assert sha
    assert is_valid_sha(sha)

    repository = options.repository or os.environ.get("MOTH_REPOSITORY")

    target_path = join(to_db_path(root_path), sha[0:3], sha)
    ensure(sha, repository, target_path)

    manifest = util.read_manifest(root_path)
    if not manifest.get("aliases"):
        manifest["aliases"] = {}
    exists = bool(manifest["aliases"].get(options.alias))
    if not manifest["aliases"].get(options.alias):
        manifest["aliases"][options.alias] = {}

    if manifest["aliases"].get(options.alias, {}).get("sha") == sha:
        print "Alias already up to date"
        return

    if exists:
        print "Updating alias:", options.alias
    else:
        print "Creating alias:", options.alias

    manifest["aliases"][options.alias]["sha"] = sha

    util.write_manifest(manifest, root_path)


def help_message():
    # Remember to update README.md as well!

    print '''
usage: moth <command> [args]

Getting started

  init      Initialize moth project in current directory
  version   Print current moth version

Managing data

  put       Put object
  alias     Add or update alias

Retrieving data

  show      Read object
'''[1:-1]


def run(base_fn):
    try:
        parser = OptionParser()
        parser.add_option("--repository", dest="repository")
        parser.add_option("--input-file", dest="input_file")
        parser.add_option("--output-file", dest="output_file")
        parser.add_option("--sha", dest="sha")
        parser.add_option("--alias", dest="alias")
        parser.add_option("--find", dest="find")
        parser.add_option("--workspace", dest="workspace", action="store_true")
        parser.add_option("--cat", dest="cat", action="store_true")
        (options, args) = parser.parse_args()

        if len(args) == 0:
            action = "default"
        elif len(args) > 1:
            fail("Too many positional arguments")
        else:
            action = args[0]

        if action == "put":
            put(options)
        elif action == "get":
            get(options)
        elif action == "show":
            show(util.find_root(base_fn), options)
        elif action == "init":
            init(options)
        elif action == "alias":
            action_alias(util.find_root(base_fn), options)
        elif action == "version":
            print "moth", str(moth.version.MAJOR) + "." + str(moth.version.MINOR)
        elif action in ["default", "help"]:
            help_message()
        else:
            fail("Unknown action: " + action)
            sys.exit(1)
    except UsageException as e:
        sys.stderr.write("Error: " + e.message + "\n")
        sys.exit(1)
