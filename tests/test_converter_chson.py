"""Unittests for the GABC to Volpiano converter
"""
import unittest
import json
import chant21
from music21 import converter

class TestCHSON(unittest.TestCase):
    """Tests using `syllable` as the root node"""

    def test_basic(self):
        origChant = converter.parse('(c2) A(f,g) *(:) B(fg) (::)', format='GABC')
        chson = origChant.toCHSON()
        chant = converter.parse(chson, format='CHSON', storePickle=False, forceSource=True)
        chant.flatter.show()
        print(chant)
