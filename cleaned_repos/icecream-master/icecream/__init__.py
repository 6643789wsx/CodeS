from os.path import dirname
from os.path import join as pjoin

# Import all variables in __version__.py without explicit imports.
from . import __version__
from .builtins import install, uninstall
from .icecream import *  # noqa

globals().update(dict((k, v) for k, v in __version__.__dict__.items()))
