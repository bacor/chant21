import unittest
import os
import pandas as pd
from arpeggio import visit_parse_tree as visitParseTree

# from chant21.cantus_parser import CantusParser
from music21 import converter
from chant21.parser_cantus_volpiano import ParserCantusVolpiano
from chant21.parser_cantus_text import ParserCantusText
from chant21.converter_cantus_volpiano import VisitorCantusVolpiano
from chant21.converter_cantus_volpiano import addCantusMetadataToChant
from chant21.converter_cantus_volpiano import convertCantusData

class TestCantusExamplesConversion(unittest.TestCase):
    def test_parse_volpiano_examples(self):
        """Test whether the volpiano of all Cantus examples can be parsed"""
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            parser = ParserCantusVolpiano()
            parse = parser.parser.parse(data['volpiano'])
            self.assertTrue(True)

    def test_parse_text_examples(self):
        """Test whether the manuscript text of all Cantus examples can be 
        parsed"""
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            parser = ParserCantusText()
            parse = parser.parse(data['full_text_manuscript'])
            self.assertTrue(True)
    
    def test_convert_volpiano_examples(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            ch = converter.parse(data['volpiano'], format='cantus')
            # ch.toHTML(f'tmp/cantus-html/{idx}.html')
            self.assertTrue(True)

    def test_convert_volpiano_and_text(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            # text = data['full_text_manuscript'] #if not pd.isna(data['full_text_manuscript']) else data['incipit']
            # if pd.isna(text):
            #     input_str = data['volpiano']
            # else:
            #     input_str = data['volpiano'] + '/' + text
            try:
                ch = convertCantusData(data)
            except:
                pass
            # ch.toHTML(f'tmp/cantus-html/{idx}.html')
            # ch.show()
            self.assertTrue(True)

    def test_single_conversion_volpiano_and_text(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        idx = 'chant_003092'
        data = examples.loc[idx,:]
        
        text = data['full_text_manuscript'] #if not pd.isna(data['full_text_manuscript']) else data['incipit']
        if pd.isna(text):
            input_str = data['volpiano']
        else:
            input_str = data['volpiano'] + '/' + text
        ch = converter.parse(input_str, format='cantus')
        ch.toHTML(f'tmp/cantus-html/{idx}.html')
            # ch.show()
        self.assertTrue(True)

    def test_examples(self):
        volpiano = '1---gK--k---h--kl--k--g--g---g--j--kl--l---k---n7--l--m---kj--gh---kH--k--h--g--fg--g---g--hhhk---k---k--kj--gh--h---j--kl--lkJ--hg--g---g--h--jk---lm--ml--l--l---l-lkj--g---h--k--k---4'
        parser = ParserCantusVolpiano()
        parse = parser.parser.parse(volpiano)
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        print(chant)
    
    def test_load_metadata(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        idx = 'chant_003092'
        data = examples.loc[idx,:]
    
        ch = converter.parse(data['volpiano'], format='cantus')
        addCantusMetadataToChant(ch, data)
        ch.toHTML(f'tmp/cantus-html/{idx}.html')
            # ch.show()
        self.assertTrue(True)

    def test_incipit_example(self):
        volpiano = '1--c--ef-g-g--e--fe-d--dc-f-g'
        chant = converter.parse(volpiano, format='Cantus')
        print(chant)

if __name__ == '__main__':
    unittest.main()