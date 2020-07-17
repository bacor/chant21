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

# Make parsers and converters available to music21.converter
from .parser_gabc import ParserGABC
from .parser_cantus_volpiano import ParserCantusVolpiano
from .parser_cantus_text import ParserCantusText
from .converter_gabc import ConverterGABC
from .converter_chson import ConverterCHSON
from .converter_cantus_volpiano import ConverterCantusVolpiano