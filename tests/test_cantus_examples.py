import unittest
import os
import pandas as pd
from arpeggio import visit_parse_tree as visitParseTree

# from chant21.cantus_parser import CantusParser
from music21 import converter
from chant21.parser_cantus_volpiano import ParserCantusVolpiano
from chant21.converter_cantus_volpiano import VisitorCantusVolpiano

class TestCantusExamplesConversion(unittest.TestCase):

    def test_cantus_examples(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            ch = converter.parse(data['volpiano'], format='cantus')
            # ch.toHTML(f'tmp/cantus-html/{idx}.html')
            self.assertTrue(True)

    def test_examples(self):
        volpiano = '1---gK--k---h--kl--k--g--g---g--j--kl--l---k---n7--l--m---kj--gh---kH--k--h--g--fg--g---g--hhhk---k---k--kj--gh--h---j--kl--lkJ--hg--g---g--h--jk---lm--ml--l--l---l-lkj--g---h--k--k---4'
        parser = ParserCantusVolpiano()
        parse = parser.parser.parse(volpiano)
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        print(chant)

    def test_incipit_example(self):
        volpiano = '1--c--ef-g-g--e--fe-d--dc-f-g'
        chant = converter.parse(volpiano, format='Cantus')
        print(chant)

if __name__ == '__main__':
    unittest.main()