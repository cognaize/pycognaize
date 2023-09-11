import cloudstorageio.hooks
from cloudstorageio import CloudInterface

from ..login import Login

cloud_interface_with_login = None
cloud_interface = None


def _relogin_s3():
    login = Login()

    login.relogin()

    return (
        login.aws_access_key,
        login.aws_secret_access_key,
        login.aws_session_token
    )


def _get_ci_with_login():
    global cloud_interface_with_login
    if cloud_interface_with_login is not None:
        return cloud_interface_with_login

    login = Login()

    cloud_interface_with_login = CloudInterface(
        aws_access_key_id=login.aws_access_key,
        aws_secret_access_key=login.aws_secret_access_key,
        aws_session_token=login.aws_session_token
    )

    cloudstorageio.hooks.hook_registry.register('relogin_s3', _relogin_s3)

    return cloud_interface_with_login


def _get_ci_without_login():
    global cloud_interface
    if cloud_interface is not None:
        return cloud_interface

    cloud_interface = CloudInterface()

    cloudstorageio.hooks.hook_registry.register('relogin_s3', _relogin_s3)

    return cloud_interface


def get_cloud_interface():
    login = Login()
    if login.logged_in:
        return _get_ci_with_login()

    return _get_ci_without_login()
