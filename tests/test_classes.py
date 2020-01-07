import unittest

from volpyano.volpyano import *

class TestNeume(unittest.TestCase):

    def test_neume(self):
        a = Note('a')
        b = Note('b')
        c = Note('c')
        neume = Neume(a,b,c)

        print(neume)

class TestSyllable(unittest.TestCase):

    def test_syllable(self):

        pass

if __name__ == '__main__':
    unittest.main()