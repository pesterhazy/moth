import os
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
            self.get(sha, tmp_fname)
            remove_f(output_file)  # to avoid exceptions on win32
            os.rename(tmp_fname, output_file)
        finally:
            remove_f(tmp_fname)
