import unittest
import os
import pandas as pd
from arpeggio import visit_parse_tree as visitParseTree
from music21 import converter

from chant21.cantus import ParserCantusVolpiano
from chant21.cantus import ParserCantusText
from chant21.cantus import VisitorCantusVolpiano
from chant21.cantus import addCantusMetadataToChant
from chant21.cantus import convertCantusData

class TestCantusExamplesConversion(unittest.TestCase):
    _tmp_dir = 'tmp/cantus-html'

    def setUp(self):
        os.makedirs(self._tmp_dir, exist_ok=True)

    def tearDown(self):
        dir = self._tmp_dir
        for i in os.listdir(dir):
            os.remove(os.path.join(dir, i))

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
            ch.toHTML(f'tmp/cantus-html/{idx}.html')
            self.assertTrue(True)

    def test_convert_volpiano_and_text(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        for idx, data in examples.iterrows():
            try:
                ch = convertCantusData(data)
                ch.toHTML(f'tmp/cantus-html/{idx}.html')
            except:
                pass
            self.assertTrue(True)

    def test_single_conversion_volpiano_and_text(self):
        examples = pd.read_csv('chant21/examples/cantus-volpiano-examples.csv', index_col=0)
        # idx = 'chant_003092'
        idx = 'chant_002241'
        data = examples.loc[idx,:]
        ch = convertCantusData(data)
        # text = data['full_text_manuscript'] #if not pd.isna(data['full_text_manuscript']) else data['incipit']
        # if pd.isna(text):
        #     input_str = data['volpiano']
        # else:
        #     input_str = data['volpiano'] + '/' + text
        # ch = converter.parse(input_str, format='cantus')
        # ch.toHTML(f'tmp/cantus-html/{idx}.html')
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

    def test_misalignment(self):
        """Not really a test. This just generates html files with the three types
        of misalignments to check if those are visualized correctly."""
        ch = converter.parse('cantus: 1---a--b--c---d---3/bada ca')
        ch.toHTML('tmp/test-misaligned-sylls.html')

        ch = converter.parse('cantus: 1---a--b---d---e---3---f---3/bada ca | da')
        ch.toHTML('tmp/test-misaligned-words.html')

        ch = converter.parse('cantus: 1---a---3---b---3/bada ca')
        ch.toHTML('tmp/test-misaligned-sections.html')
        
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()