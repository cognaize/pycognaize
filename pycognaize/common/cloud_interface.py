from cloudstorageio import CloudInterface

from ..login import Login

cloud_interface_logged_in = None
cloud_interface = None


def _get_logged_in_ci():
    global cloud_interface_logged_in
    if cloud_interface_logged_in is not None:
        return cloud_interface_logged_in

    login = Login()

    cloud_interface_logged_in = CloudInterface(
        aws_access_key_id=login.aws_access_key,
        aws_secret_access_key=login.aws_secret_access_key,
        aws_session_token=login.aws_session_token
    )

    return cloud_interface_logged_in


def _get_ci_without_login():
    global cloud_interface
    if cloud_interface is not None:
        return cloud_interface

    cloud_interface = CloudInterface()

    return cloud_interface


def get_cloud_interface():
    login = Login()
    if login.logged_in:
        return _get_logged_in_ci()

    return _get_ci_without_login()
