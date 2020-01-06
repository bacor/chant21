import unittest
from gabc2volpiano import GABCParser

class TestSpecialCases(unittest.TestCase):
    """Tests of examples where parsing failed initially"""
    
    def test_clef_change(self):
        gabc = '<sp>V/</sp>.(z0::c3) Sur(hi~)ge'
        parser = GABCParser(root='body')
        parse = parser.parse(gabc)
        self.assertFalse(parse.error)

if __name__ == '__main__':
    unittest.main()