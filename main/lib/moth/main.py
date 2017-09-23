import os, sys, yaml, errno, hashlib, re, shutil
import zipfile
from os.path import join, isfile, dirname
from subprocess import check_call
from optparse import OptionParser
import moth.version
import util

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def find_vcs_root(test, dirs=(".git",)):
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    raise Exception("No project root found")

def fetch(artifact_id, version, target):
    print "Fetching:", artifact_id, version
    path = dirname(target)
    if path:
        mkdir_p(path)
        repo_dir = os.path.expanduser("~/.moth-repo")
        check_call(["cp", join(repo_dir,artifact_id,version,artifact_id), target])

def split_argv(argv):
    if '--' in argv:
        idx = argv.index('--')

        return [argv[:idx],argv[idx+1:]]
    else:
        return [argv, []]

def read_manifest(root_path):
    fname = join(root_path,"moth.yaml")

    with open(fname, 'r') as f:
        return yaml.load(f)

def run__(args):
    my_args, their_args = split_argv(args)

    action = my_args[0]
    assert action in ["run","path"]

    artifact_id = my_args[1]

    root_path = find_vcs_root(dirname(__file__))

    manifest = read_manifest(root_path)
    version = str(manifest.get("dependencies", {}).get(artifact_id))

    dot_dir = "moth_packages"

    target_fn = artifact_id

    fname = join(root_path,dot_dir,target_fn)

    if not isfile(fname):
        fetch(artifact_id, version, fname)

    if action == "run":
        os.execlp(fname, fname, *their_args)
    elif action == "path":
        print(fname)
    else:
        raise "Unknown action"

def to_repo_base(url):
    match = re.match("^file:/*(/.*$)", url)
    assert match, "Must be file URL"
    return match.group(1)

def hash_file(fn):
    return hashlib.sha1(file(fn).read()).hexdigest()

def put(options):
    assert options.repository
    assert options.input_file

    repo_base = to_repo_base(options.repository)

    sha = hash_file(options.input_file)
    target_path = join(repo_base,"db",sha[0:3],sha)
    mkdir_p(target_path)
    shutil.copy(options.input_file, join(target_path,"contents"))

    print sha

def get(options):
    assert options.repository
    assert options.sha, "Need to pass a sha"

    repo_base = to_repo_base(options.repository)
    target_path = join(repo_base,"db",options.sha[0:3],options.sha)
    shutil.copy(join(target_path,"contents"), options.output_file or "/dev/stdout")

def to_db_path(root_path):
    return join(root_path, ".moth", "db")

def copy(from_fn, to_fn):
    shutil.copy(from_fn, to_fn)

def path(root_path, options):
    target_path = join(to_db_path(root_path),"db",options.sha[0:3],options.sha)
    content_path = join(target_path, "contents")

    if not os.path.isfile(target_path):
        repo_base = to_repo_base(options.repository)
        from_path = join(repo_base,"db",options.sha[0:3],options.sha)
        mkdir_p(target_path)
        copy(join(from_path,"contents"), content_path)

    if options.workspace or options.find:
        workspace_path = join(target_path, "workspace")

        if os.path.isfile(workspace_path):
            assert os.path.isdir(workspace_path)

            zip_ref = zipfile.ZipFile(content_path, 'r')
            zip_ref.extractall(workspace_path)
            zip_ref.close()

        if options.find:
            find_path = join(workspace_path, options.find)
            print find_path
        else:
            print workspace_path
    else:
        print content_path

def run(base_fn):
    parser = OptionParser()
    parser.add_option("--repository", dest="repository", default=os.environ.get("MOTH_REPOSITORY"))
    parser.add_option("--input-file", dest="input_file")
    parser.add_option("--output-file", dest="output_file")
    parser.add_option("--sha", dest="sha")
    parser.add_option("--find", dest="find")
    parser.add_option("--workspace", dest="workspace", action="store_true")
    (options, args) = parser.parse_args()

    assert len(args) == 1, "Expecting exactly one positional argument"

    root_path = util.find_root(base_fn)
    action = args[0]

    if action == "put":
        put(options)
    elif action == "get":
        get(options)
    elif action == "path":
        path(root_path, options)
    elif action == "version":
        print "moth", str(moth.version.MAJOR) + "." + str(moth.version.MINOR)
    else:
        print "Unknown action"
        sys.exit(1)
