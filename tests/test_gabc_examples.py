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
        gabc = """(f3)TU(_e!fg)a(f) est(f') * Po(h)tén(hgh)ti(fg)a,(ffe.) (,)tu(f)um(h) re((hvG__F'E)gnum,(f!gwh/ih'hg~) Dó(f)mi(fg/hv_GF'g)ne :(gf..) (;)tu(f_iH'G___/h_vGF'g) es(g_f) su(fg)per(f') om(g>)nes(hih) gen(h_vGF'g>)tes :(ffe.) *(:)Da(h) pa(hg)cem,(f) dó(ghg)mi(ef!gvFE'f)ne,(efe___ec.) (,)in(f) di(f_hG'E)é(hv_hv_)bus(ih'hg) no(fg!hv_GF'g)stris.(gf..) <sp>V/</sp>.(::)Cre(f)á(e.f!gwh/
hi)tor(h) óm(ij~)ni(i)um,(h.) (,)De(hi)us,(h') ter(h)rí(h)bi(hg)lis(hi) et(gh) for(fgwh_g)tis,(gf..) (;)jus(f)tus(ef) et(f!gwh_G!F'E__) mi(f)sé(hg/hih)ri(hv_GF'g)cors.(ffe.) *(::)Da(h) pa(hg)cem.(f) <sp>V/</sp>. (::)Gló(e.f!gwh/hi)ri(h)a(h) Pa(hg)tri,(hi) et(gh) Fí(f)li(f!gwh_g)o,(gf..) (;)et(f) Spi(f)rí(f!gwh_G!F'E__)tu(f)i(hg/hih) San(hv_GF'g>)cto.(ffe.) *(::)Da(h) pa(hg)cem.(f) (::)"""
        parser = ParserGABC(root='body')
        parse = parser.parse(gabc)
        print(parse)
    
    def test_ex2(self):
        gabc="Re(c4f)ctor(f) (;)"
        # gabc = 'f(g) (::h+)'
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
        GABC_FN = '/Users/Bas/repos/projects/GregoBaseCorpus/gabc/{idx:0>5}.gabc'
        filename = GABC_FN.format(idx=1)
        chant = converter.parse(filename)
        self.assertFalse(parse.error)

if __name__ == '__main__':
    unittest.main()