import os
import sys
import hashlib
import re
import shutil
import zipfile
import tempfile
import json
from os.path import join, isfile, dirname
from subprocess import check_call
from optparse import OptionParser
import moth.version
import util
import fs
from urlparse import urlparse
import boto3

def croak():
    print '\xe2\x9b\x94\xef\xb8\x8f'
    sys.exit(1)


def fail(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(1)


def find_vcs_root(test, dirs=(".git",)):
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    raise Exception("No project root found")


def split_argv(argv):
    if '--' in argv:
        idx = argv.index('--')

        return [argv[:idx], argv[idx + 1:]]
    else:
        return [argv, []]


# TODO: remove
def to_repo_base(url):
    match = re.match("^file:/*(/.*$)", url)
    assert match, "Must be file URL"
    return match.group(1)


def hash_file(fn):
    return hashlib.sha1(file(fn).read()).hexdigest()


class FileProvider:
    def __init__(self, url):
        self.repo_base = self.to_repo_base(url)
        pass

    def to_repo_base(self, url):
        match = re.match("^file:/*(/.*$)", url)
        assert match, "Must be file URL"
        return match.group(1)

    def put(self, input_file):
        sha = hash_file(input_file)
        target_path = join(self.repo_base, "db", sha[0:3], sha)
        fs.mkdir_p(target_path)
        shutil.copy(input_file, join(target_path, "contents"))

        return sha


def pjoin(*args):
    return "/".join(args)


class S3Provider:
    def __init__(self, url):
        self.url_components = urlparse(url)

    def put(self, input_file):
        sha = hash_file(input_file)
        target_path = pjoin(self.url_components.path or "/",
                                "db", sha[0:3], sha)
        s3 = boto3.resource('s3', endpoint_url="http://localhost:4568", aws_access_key_id="1234", aws_secret_access_key="1234")
        s3.Bucket(self.url_components.netloc).upload_file(input_file, target_path)

        return sha


def make_provider(url):
    if url.startswith("file:"):
        return FileProvider(url)
    elif url.startswith("s3:"):
        return S3Provider(url)

    raise Exception("No match for URL type: " + url)


def put(options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")
    assert repository
    assert options.input_file

    provider = make_provider(repository)

    sha = provider.put(options.input_file)
    print sha


def get(options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")
    assert repository
    assert options.sha, "Need to pass a sha"

    repo_base = to_repo_base(repository)
    target_path = join(repo_base, "db", options.sha[0:3], options.sha)
    shutil.copy(join(target_path, "contents"),
                options.output_file or "/dev/stdout")


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
    assert repository
    content_path = join(target_path, "contents")

    if not os.path.isfile(target_path):
        repo_base = to_repo_base(repository)
        from_path = join(repo_base, "db", sha[0:3], sha)
        fs.mkdir_p(target_path)
        copy(join(from_path, "contents"), content_path)


def show(root_path, options):
    repository = options.repository or os.environ.get("MOTH_REPOSITORY")

    sha = resolve_alias(root_path, options.alias) if options.alias else options.sha
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

    assert options.repository

    data = {"repositories": [{"url": options.repository}]}

    with open("moth.json","w") as out:
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
    ensure(sha, repository,target_path)

    manifest = util.read_manifest(root_path)
    if not manifest.get("aliases"):
        manifest["aliases"] = {}
    exists = bool(manifest["aliases"].get(options.alias))
    if not manifest["aliases"].get(options.alias):
        manifest["aliases"][options.alias] = {}

    if manifest["aliases"].get(options.alias,{}).get("sha") == sha:
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
