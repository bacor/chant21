import unittest
import os
import pandas as pd
from arpeggio import visit_parse_tree as visitParseTree

# from chant21.cantus_parser import CantusParser
from music21 import converter
from chant21.parser_cantus_volpiano import ParserCantusVolpiano
from chant21.converter_cantus_volpiano import VisitorCantusVolpiano

# class TestVolpianoExamples(unittest.TestCase):
#     """Tests using `syllable` as the root node"""

#     def test_files(self):
#         examples = pd.read_csv('chant21/examples/volpiano-examples.csv')

#         parser = CantusParser()
#         numParsed = 0
#         for idx, (volpiano, text) in examples.head(1000).iterrows():
#             try:
#                 parse = parser.parse(volpiano)
#                 numParsed += 1
#                 # print(f'{idx} succesfully parsed')
#             except Exception as e:
#                 print(f'{idx} failed: {e}')
#         print(f'{numParsed} chants succesfully parsed')
#         # self.assertEqual(len(parse), 3)
#         # self.assertEqual(parse[0].rule_name, 'neume')
#         # self.assertEqual(parse[1].rule_name, 'neume_boundary')
#         # self.assertEqual(parse[2].rule_name, 'neume')

#     def test_single_examples(self):
#         # volpiano = '1---gK--k---h--kl--k--g--g---g--j--kl--l---k---n7--l--m---kj--gh---kH--k--h--g--fg--g---g--hhhk---k---k--kj--gh--h---j--kl--lkJ--hg--g---g--h--jk---lm--ml--l--l---l-lkj--g---h--k--k---6------67--g---4'
#         volpiano = '1---gK---6------67--g---4'
#         # volpiano = '1---dhj--h--h---hkhjk--h--hg-hjh---f--g---gh-kh7--ghg---fgfed--cd---de-fef--ed---d---d--fgh--g---g--g---gfg--fgfed---fgfe--fgh77---hhgfe-fgfg--gf---3---f---gh--hkh-jk--jh---ghfg---fgfed---ff--dfd-dc---fgfe--fgh--hghf-gfe---defef7--ed---4'
#         # volpiano = '1---dhj--h--h---hkhjk--h--hg-hjh---f--g---gh-kh7--ghg'
#         parser = CantusParser()
#         parse = parser.parse(volpiano)
#         print(parse)


class TestCantusExamplesConversion(unittest.TestCase):
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