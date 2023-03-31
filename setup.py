import codecs
import os.path
import re

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup_options = dict(
    license="Apache License 2.0",
    python_requires=">= 3.7",
    entry_points='''
        [console_scripts]
        cognaize=pycognaize.cli:cognaize''',
    project_urls={
        'Source': 'https://github.com/cognaize/pycognaize',
        'Reference': 'https://pycognaize.readthedocs.io/en/latest/',
        'Changelog': 'https://github.com/cognaize/pycognaize/blob/master/CHANGELOG.md',
    },
)

setup_options['console'] = ['bin/cognaize']


setup(**setup_options)
