from pathlib import Path
from typing import Union, Type

from pycognaize.file_storage.path_type_checker import (
    is_s3_path
)
from pycognaize.file_storage.s3_storage import S3Storage
from pycognaize.file_storage.storage import Storage

STORAGES = {}


def get_storage_class(key: str) -> Type[Storage]:
    classes = {'general': Storage, 's3': S3Storage}
    return classes[key]


def create_storage_instance(key: str, config=None):
    STORAGES[key] = get_storage_class(key)(config)
    return STORAGES[key]


def get_or_create(key: str, config=None):
    if key not in STORAGES:
        return create_storage_instance(key, config)
    if config is None:
        return STORAGES[key]
    return create_storage_instance(key, config)


def get_storage(path: Union[str, Path], config=None) -> Storage:
    if is_s3_path(path):
        return get_or_create('s3', config)
    else:
        return get_or_create('general', config)


__all__ = ['get_storage']
