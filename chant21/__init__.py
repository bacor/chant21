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

# Main classes
from .chant import Chant21Object
from .chant import Chant
from .chant import Section
from .chant import ChantElement
from .chant import Clef
from .chant import Word
from .chant import Syllable
from .chant import Neume
from .chant import Note
from .chant import Pausa
from .chant import PausaMinima
from .chant import PausaMinor
from .chant import PausaMajor
from .chant import PausaFinalis
from .chant import Annotation
from .chant import Alteration
from .chant import Natural
from .chant import Flat

from .chant import LineBreak
from .chant import ColumnBreak
from .chant import PageBreak

# Make GABC converter available to music21.converter
from .converterGABC import ConverterGABC
from .converterCHSON import ConverterCHSON
from .parserGABC import ParserGABC

from .converter_cantus_volpiano import ConverterCantusVolpiano