import unittest
import glob
from music21 import converter
from music21 import metadata
import chant21
from chant21 import ParserGABC
from chant21.converterGABC import VisitorGABC
from arpeggio import visit_parse_tree as visitParseTree

EXAMPLES_DIR = 'chant21/examples/'

def parseGABC(string):
    return converter.parse(string, format='gabc', forceSource=True, storePickle=False)

class TestParseExamples(unittest.TestCase):

    def runTest(self, example):
        parser = ParserGABC()
        parse = parser.parseFile(example)
        self.assertFalse(parse.error)
        return parse

    def test_salveRegina(self):
        filename = f'{EXAMPLES_DIR}an--salve_regina_simple_tone--solesmes.gabc'
        self.runTest(filename)
        
    def test_utQueantLaxis(self):
        filename = f'{EXAMPLES_DIR}hy--ut_queant_laxis--solesmes.gabc'
        self.runTest(filename)

    def test_kyrie(self):
        filename = f'{EXAMPLES_DIR}ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        self.runTest(filename)

    def test_populusSion(self):
        filename = f'{EXAMPLES_DIR}populus_sion.gabc'
        self.runTest(filename)

    def test_abOrtuSolis(self):
        filename = f'{EXAMPLES_DIR}tr--ab_ortu_solis--solesmes.gabc'
        self.runTest(filename)
        
    def _test_allExamples(self):
        parser = ParserGABC()
        examples = glob.glob(f'{EXAMPLES_DIR}*.gabc')
        for filename in examples:
            self.runTest(filename)

    def test_GBCParsing(self):
        GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/dist/gregobasecorpus-v0.3/gregobasecorpus-v0.3/gabc/{idx:0>5}.gabc'
        filename = GABC_FN.format(idx=1)
        parser = ParserGABC()
        parse = parser.parseFile(filename)
        self.assertFalse(parse.error)

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
        filename = f'{EXAMPLES_DIR}/ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        chant = parseGABC(filename)
        self.assertTrue(True)

    def test_salveRegina(self):
        filename = f'{EXAMPLES_DIR}/an--salve_regina_simple_tone--solesmes.gabc'
        chant = parseGABC(filename)
        self.assertTrue(True)
        
    def test_utQueantLaxis(self):
        filename = f'{EXAMPLES_DIR}/hy--ut_queant_laxis--solesmes.gabc'
        chant = parseGABC(filename)
        self.assertTrue(True)

    def test_populusSion(self):
        filename = f'{EXAMPLES_DIR}/populus_sion.gabc'
        chant = parseGABC(filename)
        self.assertTrue(True)

    def test_abOrtuSolis(self):
        filename = f'{EXAMPLES_DIR}/tr--ab_ortu_solis--solesmes.gabc'
        chant = parseGABC(filename)
        self.assertTrue(True)

    # def test_GBCConversion2(self):
    #     GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/gabc/{idx:0>5}.gabc'
    #     filename = GABC_FN.format(idx=7231)
    #     parser = ParserGABC()
    #     parse = parser.parseFile(filename)
    #     ch = visitParseTree(parse, VisitorGABC())
    #     # ch.show()
    #     ch.toHTML('tmp/test.html')
    #     self.assertTrue(True)

    # def test_exampleConversion(self):
    #     # gabc = "(c4) AL(dc~) *(;) <i>ij.</i>(hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffdevDCd!ewfd.)"
    #     # gabc = "(c4) AL(dc~)le(c/e'gF'EC'd)lú(dc/fg!hvGF'g)ia.(g.) *(;) <i>ij.</i>(hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffdevDCd!ewfd.) "
    #     gabc = "(c4) AL(dc~)le(c/e'gF'EC'd)lú(dc/fg!hvGF'g)ia.(g.) <sp>V/</sp>.(::) Lau(h)dem(ghG'E) Dó(fe)mi(fg)ni(gvF'EC'dw!evDCd.) (;) lo(d)qué(d/ffe/ggh)tur(fvED) os(cd) me(d!ewfd)um,(d.) (:) et(de) be(gh)ne(gh)dí(h!iwj/ki'jvH'G/h!iwjh)cat(h.) (,) o(h_ghvGF)mnis(fvED) ca(c.d!ewfd)ro(d.) (;) no(de)men(gh) san(ghgh)ctum(h.) *(,) e(h!iwj/ki'jvH'G/h!iwjh)jus.(h,hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffd/evDCd!ewfd.) (::)"
    #     parser = ParserGABC()
    #     parse = parser.parse(gabc)
    #     ch = visitParseTree(parse, GABCVisitor())
    #     ch.flatter.show()
    #     self.assertTrue(True)
        
class TestCHSONConversionExamples(unittest.TestCase):
    def runTest(self, filename):
        # Music21 by default caches parses as pickle files, we disable that here
        origChant = parseGABC(filename)
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
        filename = f'{EXAMPLES_DIR}an--salve_regina_simple_tone--solesmes.gabc'
        self.runTest(filename)
        
    def test_utQueantLaxis(self):
        filename = f'{EXAMPLES_DIR}hy--ut_queant_laxis--solesmes.gabc'
        self.runTest(filename)

    def test_kyrie(self):
        filename = f'{EXAMPLES_DIR}ky--kyrie_ad_lib_x_-_orbis_factor--solesmes.gabc'
        self.runTest(filename)

    def test_populusSion(self):
        filename = f'{EXAMPLES_DIR}populus_sion.gabc'
        self.runTest(filename)

    def test_abOrtuSolis(self):
        filename = f'{EXAMPLES_DIR}tr--ab_ortu_solis--solesmes.gabc'
        self.runTest(filename)

if __name__ == '__main__':
    unittest.main()