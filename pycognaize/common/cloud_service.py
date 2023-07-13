from typing import Optional

from cloudstorageio import CloudInterface

from pycognaize.common.decorators import relogin_if_failed


class CloudService:

    def __init__(self, ci: CloudInterface):
        self.ci = ci

    @relogin_if_failed
    def listdir(self, path: str, recursive: Optional[bool] = False,
                exclude_folders: Optional[bool] = False,
                include_files: Optional[bool] = True):
        return self.ci.listdir(path, recursive, exclude_folders, include_files)

    @relogin_if_failed
    def isdir(self, path):
        return self.ci.isdir(path)

    @relogin_if_failed
    def open(self, file_path: str, mode: Optional[str] = 'rt',
             *args, **kwargs):
        return self.ci.open(file_path, mode, *args, **kwargs)

    @relogin_if_failed
    def isfile(self, path):
        return self.ci.isfile(path)

    @relogin_if_failed
    def is_local_path(self, path):
        return self.ci.is_local_path(path)

    @relogin_if_failed
    def copy_dir(self, source_dir: str, dest_dir: str,
                 multiprocess: Optional[bool] = True,
                 continue_copy: Optional[bool] = False,
                 exclude=None
                 ):
        return self.ci.copy_dir(source_dir, dest_dir,
                                multiprocess, continue_copy,
                                exclude
                                )
