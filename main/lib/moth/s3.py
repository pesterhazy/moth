import boto3
import util
from urlparse import urlparse


class S3Provider:
    def __init__(self, url):
        self.url_components = urlparse(url)

    def put(self, input_file):
        sha = util.hash_file(input_file)
        target_path = util.pjoin(self.url_components.path or "/",
                                 "db", sha[0:3], sha)
        s3 = boto3.resource('s3', endpoint_url="http://localhost:4568",
                            aws_access_key_id="1234", aws_secret_access_key="1234")
        bucket = s3.Bucket(self.url_components.netloc)
        bucket.upload_file(input_file, target_path.lstrip("/"))

        return sha

    def get(self, sha, output_file):
        target_path = util.pjoin(self.url_components.path or "/",
                                 "db", sha[0:3], sha)
        s3 = boto3.resource('s3', endpoint_url="http://localhost:4568",
                            aws_access_key_id="1234", aws_secret_access_key="1234")
        bucket = s3.Bucket(self.url_components.netloc)
        bucket.download_file(target_path.lstrip("/"), output_file)
