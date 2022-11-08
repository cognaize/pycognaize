"""This package is a powerful python API for creating ML/DL models using
    all the data and functionality provided by the pycognaize application.
"""

__version__ = "1.2.1"

__all__ = ['Login', 'Model', 'Snapshot']

import os
from .model import Model
from .login import Login
from .document import Snapshot

name = os.path.basename(os.path.dirname(__file__))
