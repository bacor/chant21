import unittest
import glob
from music21 import converter
from chant21 import ParserGABC

class TestParseExamples(unittest.TestCase):

    def run_test(self, example):
        parser = ParserGABC()
        parse = parser.parseFile(example)
        self.assertFalse(parse.error)
        return parse

    def test_salveRegina(self):
        filename = 'examples/an--salve_regina_simple_tone--solesmes.gabc'
        self.run_test(filename)
        
    def test_utQueantLaxis(self):
        filename = 'examples/hy--ut_queant_laxis--solesmes.gabc'
        self.run_test(filename)

    def test_kyrie(self):
        filename = 'examples/ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        self.run_test(filename)

    def test_populusSion(self):
        filename = 'examples/populus_sion.gabc'
        self.run_test(filename)

    def test_abOrtuSolis(self):
        filename = 'examples/tr--ab_ortu_solis--solesmes.gabc'
        self.run_test(filename)
        
    def _test_allExamples(self):
        parser = ParserGABC()
        examples = glob.glob('examples/*.gabc')
        for filename in examples:
            self.run_test(filename)

class TestSpecialCases(unittest.TestCase):
    """Tests of examples where parsing failed initially"""
    
    def _test_clefChange(self):
        gabc = '<sp>V/</sp>.(z0::c3) Sur(hi~)ge'
        parser = ParserGABC(root='body')
        parse = parser.parse(gabc)
        self.assertFalse(parse.error)

    def _test_polyphony(self):
        gabc = 'Quó(dh)ni(h)am(jhhghvG{ix}Ef_g//eg!ivHGhvFDe.)'
        parser = ParserGABC(root='body')
        parse = parser.parse(gabc)
        self.assertFalse(parse.error)


class TestConvertExamples(unittest.TestCase):
    def test_kyrie(self):
        filename = 'examples/ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        chant = converter.parse(filename)
        self.assertTrue(True)

    def test_salveRegina(self):
        filename = 'examples/an--salve_regina_simple_tone--solesmes.gabc'
        chant = converter.parse(filename)
        self.assertTrue(True)
        
    def test_utQueantLaxis(self):
        filename = 'examples/hy--ut_queant_laxis--solesmes.gabc'
        chant = converter.parse(filename)
        self.assertTrue(True)

    def test_populusSion(self):
        filename = 'examples/populus_sion.gabc'
        chant = converter.parse(filename)
        self.assertTrue(True)

    def test_abOrtuSolis(self):
        filename = 'examples/tr--ab_ortu_solis--solesmes.gabc'
        chant = converter.parse(filename)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()