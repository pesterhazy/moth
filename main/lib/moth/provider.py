import os
import sys
import stat
import util
import string
import random


def rand8():
    return ''.join(random.choice(string.ascii_uppercase +
                                 string.ascii_lowercase +
                                 string.digits)
                   for _ in range(8))


def remove_f(f):
    if os.path.exists(f):
        os.remove(f)


class Provider():
    def safe_get(self, sha, output_file):
        tmp_fname = os.path.join(os.path.dirname(output_file),
                                 "dl." + rand8())
        try:
            self.verified_get(sha, tmp_fname)
            remove_f(output_file)  # to avoid exceptions on win32
            os.rename(tmp_fname, output_file)
        finally:
            remove_f(tmp_fname)

    def verified_get(self, sha, output_file):
        self.get(sha, output_file)

        if stat.S_ISREG(os.stat(output_file).st_mode):
            actual_sha = util.hash_file(output_file)

            if actual_sha != sha:
                raise Exception("Hash of downloaded file does not match"
                                + " expected sha: "
                                + actual_sha + " vs " + sha)
        else:
            sys.stderr.write("Skipping verification because output is " +
                             "not a regular file")
            sys.stderr.flush()
