from pathlib import Path
from typing import Union, Type

from pycognaize.file_storage.local_storage import LocalStorage
from pycognaize.file_storage.path_type_checker import is_local_path, is_s3_path
from pycognaize.file_storage.s3_storage import S3Storage
from pycognaize.file_storage.storage import Storage

storages = {}


def get_storage_class(key: str) -> Type[Storage]:
    classes = {
        'local': LocalStorage,
        's3': S3Storage
    }

    return classes[key]


def create_storage_instance(key: str, config=None):
    storage_class = get_storage_class(key)
    storage_instance = storage_class(config)
    storages[key] = storage_instance
    return storage_instance


def get_or_create(key: str, config=None):
    if key not in storages:
        return create_storage_instance(key, config)

    if config is None:
        return storages[key]

    return create_storage_instance(key, config)


def get_storage(path: Union[str, Path], config=None) -> Storage:
    if is_local_path(path):
        return get_or_create('local', config)

    if is_s3_path(path):
        return get_or_create('s3', config)

    raise ValueError('Path should be local or S3.')


__all__ = ['get_storage']
