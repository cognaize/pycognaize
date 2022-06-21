import warnings
import pycognaize


def module_not_found(stack_level: int = 2):
    """
    Warns user that function uses a module that is not listed in
    requirements.txt and is not installed in the environment

    :param stack_level: stack level of the warning
    :type stack_level: int
    """
    def module_not_found_custom(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ModuleNotFoundError as e:
                message = f"Please install module " \
                          f"{str(e).split(' ')[-1]}. \n"\
                          f"It can be found in model-requirements.txt"
                warnings.warn(message, UserWarning, stacklevel=stack_level)
        return wrapper
    return module_not_found_custom


def soon_be_deprecated(version: str = None, stack_level: int = 2):
    """
    Warns user that the function they use will soon be deprecated.


    :param version: version after which the function will be deprecated
    :type version: str
    :param stack_level: stack level of the warning
    :type stack_level: int
    """
    if version is None:
        old_version = pycognaize.__version__.split(".")
        version = f"{old_version[0]}.{str(int(old_version[1]) + 1)}.0"

    def soon_be_deprecated_custom(func):
        def wrapper(*args, **kwargs):
            message = f"This function will be deprecated after " \
                      f"version {version}"
            warnings.warn(message, DeprecationWarning, stacklevel=stack_level)
            return func(*args, **kwargs)
        return wrapper
    return soon_be_deprecated_custom
