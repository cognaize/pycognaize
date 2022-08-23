"""This package is a powerful python API for creating ML/DL models using
    all the data and functionality provided by the pycognaize application.
"""

__version__ = "1.0.2"

__all__ = ['Model', 'Snapshot']

import os
from .model import Model
from .document import Snapshot

name = os.path.basename(os.path.dirname(__file__))
