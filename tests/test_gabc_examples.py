import unittest
import glob
from music21 import converter
from music21 import metadata
from arpeggio import visit_parse_tree as visitParseTree
import chant21
from chant21.gabc import ParserGABC
from chant21.gabc import VisitorGABC
from chant21.examples import salveRegina
from chant21.examples import abOrtuSolis
from chant21.examples import kyrie
from chant21.examples import utQueantLaxis

def convertGABC(string):
    return converter.parse(string, format='gabc', forceSource=True, storePickle=False)

class TestParseExamples(unittest.TestCase):

    def runTest(self, example):
        parser = ParserGABC()
        parse = parser.parseFile(example)
        self.assertFalse(parse.error)
        return parse

    def test_salveRegina(self):
        self.runTest(salveRegina)
        
    def test_utQueantLaxis(self):
        self.runTest(utQueantLaxis)

    def test_kyrie(self):
        self.runTest(kyrie)

    def test_abOrtuSolis(self):
        self.runTest(abOrtuSolis)
        
    # def _test_allExamples(self):
    #     parser = ParserGABC()
    #     for filename in [salveRegina, utQueantLaxis, kyrie, abOrtuSolis]:
    #         self.runTest(filename)

    # def test_GBCParsing(self):
    #     GABC_FN = '../GregoBaseCorpus/dist/gregobasecorpus-v0.3/gregobasecorpus-v0.3/gabc/{idx:0>5}.gabc'
    #     filename = GABC_FN.format(idx=1)
    #     parser = ParserGABC()
    #     parse = parser.parseFile(filename)
    #     self.assertFalse(parse.error)

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
        chant = convertGABC(kyrie)
        self.assertTrue(True)

    def test_salveRegina(self):
        chant = convertGABC(salveRegina)
        self.assertTrue(True)
        
    def test_utQueantLaxis(self):
        chant = convertGABC(utQueantLaxis)
        self.assertTrue(True)

    def test_abOrtuSolis(self):
        chant = convertGABC(abOrtuSolis)
        self.assertTrue(True)

    # def test_exampleConversion(self):
    #     gabc = "(cb3) AL(d.f!gwhhv//ikkvJ'IH'Ghih'h)ma(fef.) *(,) Re(h)dem(h')ptó(d)ris(ef) Ma(gvED)ter,(d.)"        ch = converter.parse(gabc, format='gabc', forceSource=True, storePickle=False)
    #     ch.toHTML('tmp/html-test-bla.html')
    #     # parse = parser.parse(gabc)
    #     # ch = visitParseTree(parse, GABCVisitor())
    #     # ch.flatter.show()
    #     # self.assertTrue(True)
        
class TestCHSONConversionExamples(unittest.TestCase):
    def runTest(self, filename):
        # Music21 by default caches parses as pickle files, we disable that here
        origChant = convertGABC(filename)
        chson = origChant.toCHSON()
        chant = converter.parse(chson, format='chson',  forceSource=True, storePickle=False)
        for orig1, copy1 in zip(origChant, chant):
            self.assertIsInstance(copy1, type(orig1))
            if hasattr(orig1, 'elements'):
                self.assertTrue(hasattr(copy1, 'elements'))
                for orig2, copy2 in zip(orig1, copy1):
                    self.assertIsInstance(copy2, type(orig2))
                    if hasattr(orig2, 'elements'):
                        self.assertTrue(hasattr(copy2, 'elements'))
                        for orig3, copy3 in zip(orig2, copy2):
                            self.assertIsInstance(copy3, type(orig3))
                            if hasattr(orig3, 'elements'):
                                self.assertTrue(hasattr(copy3, 'elements'))
                                for orig4, copy4 in zip(orig3, copy3):
                                    self.assertIsInstance(copy2, type(orig2))
    
    def test_salveRegina(self):
        self.runTest(salveRegina)
        
    def test_utQueantLaxis(self):
        self.runTest(utQueantLaxis)

    def test_kyrie(self):
        self.runTest(kyrie)

    def test_abOrtuSolis(self):
        self.runTest(abOrtuSolis)

if __name__ == '__main__':
    unittest.main()