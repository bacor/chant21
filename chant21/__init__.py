# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         __init__.py
# Purpose:      the main file of chant21
#
# Authors:      Bas Cornelissen
#
# Copyright:    Copyright © 2020-present Bas Cornelissen
# License:      see LICENSE
# ------------------------------------------------------------------------------

# Get version from _version.py; this approach is copied from music21
from ._version import __version__

# Make parsers and converters available to music21.converter
from .gabc import *
from .cantus import *
from .chson import *

# Don't import .chant to encourage the use of 'from chant21 import chant', 
# and then use things like chant.Note to distinguishes the chant21 classes
# from music21 classes.