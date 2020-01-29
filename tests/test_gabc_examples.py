import unittest
import glob
from music21 import converter
from chant21 import ParserGABC
from chant21.converterGABC import GABCVisitor
from arpeggio import visit_parse_tree as visitParseTree
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

    def test_GBCParsing(self):
        GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/gabc/{idx:0>5}.gabc'
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

    def test_ex(self):
        gabc = 'f(g) (::h+)'
        parser = ParserGABC(root='body')
        parse = parser.parse(gabc, debug=True)
        print(parse)

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

    def test_GBCConversion(self):
        # GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/gabc/{idx:0>5}.gabc'
        GABC_FN = '/Users/Bas/Dropbox/Desktop/gabc/{idx:0>5}.gabc'
        filename = GABC_FN.format(idx=1)
        ch = converter.parse(filename)
        ch.flatter.show()
        self.assertTrue(True)

    def test_GBCConversion2(self):
        GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/gabc/{idx:0>5}.gabc'
        filename = GABC_FN.format(idx=4)
        parser = ParserGABC()
        parse = parser.parseFile(filename)
        ch = visitParseTree(parse, GABCVisitor())
        ch.toCHSON('test.json')
        ch.flatter.show()
        self.assertTrue(True)

    def test_exampleConversion(self):
        # gabc = "(c4) AL(dc~) *(;) <i>ij.</i>(hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffdevDCd!ewfd.)"
        # gabc = "(c4) AL(dc~)le(c/e'gF'EC'd)lú(dc/fg!hvGF'g)ia.(g.) *(;) <i>ij.</i>(hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffdevDCd!ewfd.) "
        gabc = "(c4) AL(dc~)le(c/e'gF'EC'd)lú(dc/fg!hvGF'g)ia.(g.) <sp>V/</sp>.(::) Lau(h)dem(ghG'E) Dó(fe)mi(fg)ni(gvF'EC'dw!evDCd.) (;) lo(d)qué(d/ffe/ggh)tur(fvED) os(cd) me(d!ewfd)um,(d.) (:) et(de) be(gh)ne(gh)dí(h!iwj/ki'jvH'G/h!iwjh)cat(h.) (,) o(h_ghvGF)mnis(fvED) ca(c.d!ewfd)ro(d.) (;) no(de)men(gh) san(ghgh)ctum(h.) *(,) e(h!iwj/ki'jvH'G/h!iwjh)jus.(h,hghvGFg_fgvFDffdev.dec.,e/ggh'GFgvFEffd/evDCd!ewfd.) (::)"
        parser = ParserGABC()
        parse = parser.parse(gabc)
        ch = visitParseTree(parse, GABCVisitor())
        ch.flatter.show()
        self.assertTrue(True)
        

if __name__ == '__main__':
    unittest.main()