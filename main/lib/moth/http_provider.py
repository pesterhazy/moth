import util
import requests
from clint.textui import progress



class HTTPProvider:
    def __init__(self, url):
        self.url = url

    def upload(self, frm, to):
        raise Exception("HTTPProvider cannot be used to upload objects")

    def download(self, frm, to):
        chunk_size = 1024

        r = requests.get(frm, stream=True)
        r.raise_for_status()
        with open(to, 'wb') as f:
            content_length = r.headers.get('content-length')

            if content_length:
                total_length = int(content_length)
                for chunk in progress.bar(r.iter_content(chunk_size=chunk_size),
                                          expected_size=(total_length/chunk_size) + 1):
                    if chunk:
                        f.write(chunk)
            else:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)

    def put(self, input_file):
        sha = util.hash_file(input_file)
        target_path = util.pjoin(self.url, "db", sha[0:3], sha, "contents")
        self.upload(input_file, target_path)

        return sha

    def get(self, sha, output_file):
        target_path = util.pjoin(self.url, "db", sha[0:3], sha, "contents")
        self.download(target_path, output_file)
