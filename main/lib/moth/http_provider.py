import requests
import util


class HTTPProvider:
    def __init__(self, url):
        self.url = url

    def upload(self, frm, to):
        raise Exception("HTTPProvider cannot be used to upload objects")

    def download(self, frm, to):
        assert False, "Boom"

    def put(self, input_file):
        sha = util.hash_file(input_file)
        target_path = util.pjoin(self.url, "db", sha[0:3], sha)
        self.upload(input_file, target_path)

        return sha

    def get(self, sha, output_file):
        target_path = util.pjoin(self.url, "db", sha[0:3], sha)
        self.download(target_path, output_file)
