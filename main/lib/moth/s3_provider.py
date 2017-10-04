import boto3
import util
import os
import provider
from urlparse import urlparse


class S3Provider(provider.Provider):
    def __init__(self, url):
        self.url_components = urlparse(url)
        opts = {}
        if os.environ.get("MOTH_S3_ENDPOINT") is not None:
            opts["endpoint_url"] = os.environ.get("MOTH_S3_ENDPOINT")
        self.s3 = boto3.resource('s3', **opts)
        self.bucket = self.s3.Bucket(self.url_components.netloc)

    def put(self, input_file):
        sha = util.hash_file(input_file)
        target_path = util.pjoin(self.url_components.path or "/",
                                 "db", sha[0:3], sha, "contents")
        self.bucket.upload_file(input_file, target_path.lstrip("/"))

        return sha

    def get(self, sha, output_file):
        target_path = util.pjoin(self.url_components.path or "/",
                                 "db", sha[0:3], sha, "contents")
        self.bucket.download_file(target_path.lstrip("/"), output_file)
