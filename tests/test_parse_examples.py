import unittest
import glob
from pygabc.parser import GABCParser

def run_test(self, example):
    parser = GABCParser()
    parse = parser.parse_file(example)
    self.assertFalse(parse.error)
    return parse

class TestParseExamples(unittest.TestCase):

    def run_test(self, example):
        parser = GABCParser()
        parse = parser.parse_file(example)
        self.assertFalse(parse.error)
        return parse

    def test_salve_regina(self):
        filename = 'examples/an--salve_regina_simple_tone--solesmes.gabc'
        self.run_test(filename)
        
    def test_ut_queant_laxis(self):
        filename = 'examples/hy--ut_queant_laxis--solesmes.gabc'
        self.run_test(filename)

    def test_kyrie(self):
        filename = 'examples/ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        self.run_test(filename)

    def test_populus_sion(self):
        filename = 'examples/populus_sion.gabc'
        self.run_test(filename)

    def test_ab_ortu_solis(self):
        filename = 'examples/tr--ab_ortu_solis--solesmes.gabc'
        self.run_test(filename)
        
    def test_all_examples(self):
        parser = GABCParser()
        examples = glob.glob('examples/*.gabc')
        for filename in examples:
            self.run_test(filename)
        
if __name__ == '__main__':
    unittest.main()