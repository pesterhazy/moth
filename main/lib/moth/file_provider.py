import re
import util
import fs
import shutil
import os.path


class FileProvider:
    def __init__(self, url):
        self.repo_base = self.to_repo_base(url)
        pass

    def to_repo_base(self, url):
        match = re.match("^file:/*(/.*$)", url)
        assert match, "Must be file URL"
        return match.group(1)

    def put(self, input_file):
        sha = util.hash_file(input_file)
        target_path = os.path.join(self.repo_base, "db", sha[0:3], sha)
        fs.mkdir_p(target_path)
        shutil.copy(input_file, os.path.join(target_path, "contents"))

        return sha

    def get(self, sha, output_file):
        target_path = os.path.join(self.repo_base, "db", sha[0:3], sha)
        shutil.copy(os.path.join(target_path, "contents"), output_file)
