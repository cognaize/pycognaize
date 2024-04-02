from cloudpathlib import S3Client
from pycognaize.file_storage.storage import Storage


class S3Storage(Storage):

    def __init__(self, config=None):
        super().__init__(config)
        if config is not None:
            client = S3Client(
                aws_access_key_id=config['aws_access_key_id'],
                aws_session_token=config['aws_session_token'],
                aws_secret_access_key=config['aws_secret_access_key']
            )
            client.set_as_default_client()
