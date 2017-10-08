import util
import provider
from util import UsageException
import requests
from clint.textui import progress


def process_progress(f, r, chunk_size, content_length):
    total_length = int(content_length)
    for chunk in progress.bar(r.iter_content(chunk_size=chunk_size),
                              expected_size=(total_length/chunk_size) + 1):
        if chunk:
            f.write(chunk)


def process(f, r, chunk_size):
    for chunk in r.iter_content(chunk_size=chunk_size):
        f.write(chunk)


class HTTPProvider(provider.Provider):
    def __init__(self, url):
        self.url = url

    def download(self, frm, to):
        chunk_size = 1024

        r = requests.get(frm, stream=True)
        r.raise_for_status()
        with open(to, 'wb') as f:
            content_length = r.headers.get('content-length')

            if content_length and not f.isatty():
                process_progress(f=f, r=r, content_length=content_length,
                                 chunk_size=chunk_size)
            else:
                process(f=f, r=r, chunk_size=chunk_size)

    def put(self, input_file):
        raise UsageException("HTTPProvider cannot be used to upload objects")

    def get(self, sha, output_file):
        target_path = util.pjoin(self.url.rstrip("/"),
                                 "db", sha[0:3], sha, "contents")
        self.download(target_path, output_file)
