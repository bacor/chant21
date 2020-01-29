"""Unittests for the GABC PEG grammar

Author: Bas Cornelissen
Date: 27 December 2019

TODO
    * Test advanced music: code
    * Test advanced music: choral_sign
    * Test advanced music: translation
"""
import unittest
from arpeggio import NoMatch
from chant21 import ParserGABC

class TestFile(unittest.TestCase):
    def test_file(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\nattr2:value2;\n%%\n\na(f)b(g) c(h)\ni(j)'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[1].rule_name, 'separator')
        self.assertEqual(parse[2].rule_name, 'body')
        self.assertEqual(parse[3].rule_name, 'EOF')

    def test_emptyHeader(self):
        parser = ParserGABC()
        fileStr = '%%\na(f)b(g)'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'separator')
        self.assertEqual(parse[1].rule_name, 'body')
        self.assertEqual(parse[1].value, 'a | ( | f | ) | b | ( | g | ) | ')
    
    def test_emptyBody(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\n%%\n'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].rule_name, 'header')
        self.assertEqual(parse[1].rule_name, 'separator')
        self.assertEqual(parse[2].rule_name, 'EOF')

    def test_emptyHeaderAndBody(self):
        parser = ParserGABC()
        fileStr = '%%\n'
        parse = parser.parse(fileStr)
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'EOF')

    def test_bodyConfusedForHeader(self):
        """Tests that the body is not confused for the header when it contains
        both colons and semicolons"""
        parser = ParserGABC(root='file')
        parse = parser.parse('%%\na :(g) (;)')
        self.assertEqual(parse[0].value, '%%\n')
        self.assertEqual(parse[1].rule_name, 'body')
        self.assertEqual(parse[2].rule_name, 'EOF')
    
    def test_multipleHeaders(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\n%%\nattr2:value2;\n%%\n(c2) A(f)'
        parse = parser.parse(fileStr)
        h1, sep1, h2, sep2, body, _ = parse
        self.assertEqual(h1.rule_name, 'header')
        self.assertEqual(h1.value, 'attr1 | : | value1 | ;\n')
        self.assertEqual(sep1.rule_name, 'separator')
        self.assertEqual(h2.rule_name, 'header')
        self.assertEqual(h2.value, 'attr2 | : | value2 | ;\n')
        self.assertEqual(sep2.rule_name, 'separator')
        self.assertEqual(body.rule_name, 'body')

class TestHeader(unittest.TestCase):

    def test_header(self):
        parser = ParserGABC(root='header')
        header_str = "attr1: value1;\n\nattr2:value2;"
        parse = parser.parse(header_str)
        
        # Attribute 1
        attr1 = parse[0]
        self.assertEqual(attr1.rule_name, 'attribute')
        # Key
        self.assertEqual(attr1[0].rule_name, 'attribute_key')
        self.assertEqual(attr1[0].value, 'attr1')
        # Separator: colon
        self.assertEqual(attr1[1].value, ': ')
        # Value
        self.assertEqual(attr1[2].rule_name, 'attribute_value')
        self.assertEqual(attr1[2].value, 'value1')
        # Attribute end
        self.assertEqual(attr1[3].value, ';\n\n')

        # Attribute 2
        attr2 = parse[1]
        self.assertEqual(attr2.rule_name, 'attribute')
        # Key
        self.assertEqual(attr2[0].rule_name, 'attribute_key')
        self.assertEqual(attr2[0].value, 'attr2')
        # Separator: colon
        self.assertEqual(attr2[1].value, ':')
        # Value
        self.assertEqual(attr2[2].rule_name, 'attribute_value')
        self.assertEqual(attr2[2].value, 'value2')
        # Attribute end
        self.assertEqual(attr2[3].value, ';')

    def test_bracketsSpaces(self):
        parser = ParserGABC(root='header')
        headerStr = "attr1:value1 (test);"
        parse = parser.parse(headerStr)
        self.assertFalse(parse.error)

    def test_semicolons(self):
        parser = ParserGABC(root='header')
        headerStr = "attr1:value1; value2;"
        parse = parser.parse(headerStr)
        self.assertEqual(parse[0][2].value, 'value1; value2')
        # TODO test raises error when not followed by space

class TestBody(unittest.TestCase):
    def test_body(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('A(f)B(g) C(h)')
        self.assertEqual(parse.rule_name, 'body')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

    def test_otherWhitespace(self):
        parser = ParserGABC(root='body')
        spaces = [' ', '\n', '\t', '\f', '\v', '\r', '  ', '\n   \t']
        for space in spaces:
            parse = parser.parse('A(f)' + space)
            self.assertEqual(parse[0].rule_name, 'word')
            self.assertEqual(parse[0].value, 'A | ( | f | )')
            self.assertEqual(parse[1].rule_name, 'whitespace')
            self.assertEqual(parse[1].value, space)

    def test_wordsWithSpaces(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('A(f)B (g) C(h)')
        self.assertEqual(parse[0].rule_name, 'word')
        self.assertEqual(parse[0].value, 'A | ( | f | ) | B  | ( | g | )')
        self.assertEqual(parse[1].rule_name, 'whitespace')
        self.assertEqual(parse[2].rule_name, 'word')
        self.assertEqual(parse[2].value, 'C | ( | h | )')

class TestWord(unittest.TestCase):
    def test_word(self):
        parser = ParserGABC(root='word')
        parse = parser.parse('A(f)B(g)')

        self.assertEqual(parse.rule_name, 'word')
        # First syllable
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A | ( | f | )')
        # second syllable
        self.assertEqual(parse[1].rule_name, 'syllable')
        self.assertEqual(parse[1].value, 'B | ( | g | )')

    def test_wordWithSpaces(self):
        parser = ParserGABC(root='word')
        parse = parser.parse('A (f)B(g)')
        self.assertEqual(parse.rule_name, 'word')
        self.assertEqual(parse[0].rule_name, 'syllable')
        self.assertEqual(parse[0].value, 'A  | ( | f | )')

class TestClefsAndPausas(unittest.TestCase):
    def test_clefTypes(self):
        parser = ParserGABC(root='clef')
        clefs = 'c1 c2 c3 c4 f1 f2 f3 f4 cb3'.split()
        for clef_str in clefs:
            parse = parser.parse(clef_str)
            self.assertEqual(parse.rule_name, 'clef')
            self.assertEqual(parse.value, clef_str)

    def test_clefChange(self):
        # http://gregorio-project.github.io/gabc/details.html#endofline
        parser = ParserGABC(root='music')
        for gabc in ['z::c3', 'z0::c3']:
            parse = parser.parse(gabc)
            lineEnd, bar, clef = parse
            self.assertEqual(lineEnd.rule_name, 'end_of_line')
            self.assertEqual(bar.rule_name, 'pausa')
            self.assertEqual(clef.rule_name, 'clef')

    def test_clefsFollowedByMusic(self):
        # TODO remove test?
        parser = ParserGABC(root='word')
        s1, s2 = parser.parse('(c4)a(fg)')
        _, clef, _ = s1
        self.assertEqual(clef.rule_name, 'music')
        self.assertEqual(clef[0].rule_name, 'clef')

    def test_custos(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('::i+')
        bar, custos = parse
        self.assertEqual(custos.rule_name, 'custos')
        self.assertEqual(custos.value, 'i+')
    
    def test_emptyCustos(self):
        """Custos without position, makes no sense, but included anyway"""
        parser = ParserGABC(root='music')
        parse = parser.parse('::+')
        bar, custos = parse
        self.assertEqual(custos.rule_name, 'custos')
        self.assertEqual(custos.value, '+')

class TestSyllable(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSyllable, self).__init__(*args, **kwargs)
        self.parser = ParserGABC(root='syllable')

    def test_textMusic(self):
        parse = self.parser.parse('a_string(fgf)')

        self.assertEqual(parse.rule_name, 'syllable')
        self.assertEqual(parse[0].rule_name, 'text')
        self.assertEqual(parse[0].value, 'a_string')
        self.assertEqual(parse[1].value, '(')
        self.assertEqual(parse[2].rule_name, 'music')
        self.assertEqual(parse[3].value, ')')
    
        self.assertEqual(parse[2][0].rule_name, 'note')
        self.assertEqual(parse[2][1].rule_name, 'note')
        self.assertEqual(parse[2][2].rule_name, 'note')

        self.assertEqual(parse[2][0][0].rule_name, 'position')
        self.assertEqual(parse[2][0][0].value, 'f')

    def test_spaces(self):
        """Test whether a syllable starting with a space does not match"""
        self.assertRaises(NoMatch, lambda: self.parser.parse(' a(f)'))

    def test_spacesInMusic(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('f , g')
        n1, sp1, comma, sp2, n2 = parse
        self.assertEqual(sp1.rule_name, 'spacer')
        self.assertEqual(comma.rule_name, 'pausa')
        self.assertEqual(comma.value, ',')
        self.assertEqual(sp2.rule_name, 'spacer')

class TestAdvanced(unittest.TestCase):
    
    def test_accidental(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('fxgwf')
        self.assertEqual(len(parse), 3)
        self.assertEqual(parse[0].rule_name, 'alteration')
        self.assertEqual(parse[1].rule_name, 'note')
        self.assertEqual(parse[2].rule_name, 'note')

    def test_polyphony(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('{i}')
        self.assertEqual(parse[0].rule_name, 'polyphony')

    def test_braces(self):
        braces = [
            '[ob:1]',
            '[ob:1;6mm]',
            '[ocb:1;18mm]',
            '[ocb:1;18.1235mm]',
            '[ocba:1{]',
            '[ocba:0}]',
        ]
        parser = ParserGABC(root='music')
        for gabc in braces: 
            parse = parser.parse(gabc)
            self.assertEqual(parse.rule_name, 'music')
            self.assertEqual(parse[0].rule_name, 'brace')
            self.assertEqual(parse[0].value, gabc)

    def test_verbatimCode(self):
        parser = ParserGABC(root='code')
        codeExamples = [
            '[nv:\mycode]', 
            '[gv:\mycode]', 
            '[ev:\mycode]', 
        ]
        for code in codeExamples:
            parse = parser.parse(code)
            self.assertEqual(parse.rule_name, 'code')
            self.assertEqual(parse[1].rule_name, 'verbatim_code')
    
    def test_macroReferences(self):
        parser = ParserGABC(root='code')
        codeExamples = ['[nm1]', '[gm1]', '[em1]']
        for code in codeExamples:
            parse = parser.parse(code)
            self.assertEqual(parse.rule_name, 'code')
            self.assertEqual(parse[1].rule_name, 'macro_reference')

    def test_macroAboveBody(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(c2) def-m1:\grealign;\ndef-m2:\grealign;\na(f)')
        clef, _, macro1, _, macro2, _, word, _ = parse
        self.assertEqual(macro1.rule_name, 'macro')
        self.assertEqual(macro2.rule_name, 'macro')
        
class TestNote(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestNote, self).__init__(*args, **kwargs)
        self.parser = ParserGABC(root='note')
        
    def test_positions(self):
        for position in 'abcdefghijklm':
            parse = self.parser.parse(position)
            self.assertEqual(parse.rule_name, 'note')
            self.assertEqual(parse[0].rule_name, 'position')
            self.assertEqual(parse[0].value, position)

    def test_accents(self):
        parse = self.parser.parse('gr1')

        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'r1')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr2")
        self.assertEqual(parse[1].value, "r2")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr3")
        self.assertEqual(parse[1].value, "r3")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr4")
        self.assertEqual(parse[1].value, "r4")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr5")
        self.assertEqual(parse[1].value, "r5")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        # Multiple 
        parse = self.parser.parse("gr0r3")
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')
        self.assertEqual(parse[1][0].value, "r0")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')
        self.assertEqual(parse[1][1].value, "r3")
        self.assertEqual(parse[1][1].rule_name, 'empty_note_or_accent')

    def test_emptyNotes(self):
        parse = self.parser.parse('gr')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'r')
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gR")
        self.assertEqual(parse[1].value, "R")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

        parse = self.parser.parse("gr0")
        self.assertEqual(parse[1].value, "r0")
        self.assertEqual(parse[1][0].rule_name, 'empty_note_or_accent')

    def test_rhythmicSigns(self):
        parse = self.parser.parse('g_')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'g')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '_')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('g..')
        self.assertEqual(parse[1].value, '..')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('g..')
        self.assertEqual(parse[1].value, '..')
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse("g'")
        self.assertEqual(parse[1].value, "'")
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse("g'1")
        self.assertEqual(parse[1].value, "'1")
        self.assertEqual(parse[1][0].rule_name, 'rhythmic_sign')

        parse = self.parser.parse('H_502')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'H')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '_502')

    def test_oneNoteNeumes(self):
        # Test single suffix
        parse = self.parser.parse('G~')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'G')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, '~')
        self.assertEqual(parse[1][0].rule_name, 'neume_shape')

        # Test two-character suffix
        parse = self.parser.parse('Go~')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[0].value, 'G')
        self.assertEqual(parse[1].rule_name, 'suffix')
        self.assertEqual(parse[1].value, 'o~')
        self.assertEqual(parse[1][0].rule_name, 'neume_shape')

        # Test all possible suffixes
        # G~ G> g~ g< g> go g~ go< gw gv gV gs gs<
        tests = [('G~', 'G', '~'), ('G>', 'G', '>'), ('g~', 'g', '~'), 
                 ('g<', 'g', '<'), ('g>', 'g', '>'), ('go', 'g', 'o'), 
                 ('g~', 'g', '~'), ('go<', 'g', 'o<'), ('gw', 'g', 'w'),
                 ('gv', 'g', 'v'), ('gV', 'g', 'V'), ('gs', 'g', 's'),
                 ('gs<', 'g', 's<')]
        for string, position, suffix in tests:
            parse = self.parser.parse(string)
            self.assertEqual(parse[0].rule_name, 'position')
            self.assertEqual(parse[0].value, position)
            self.assertEqual(parse[1].value, suffix)
            self.assertEqual(parse[1][0].rule_name, 'neume_shape')

class TestAlterations(unittest.TestCase):
    
    def test_alteration(self):
        parser = ParserGABC(root='alteration')
        parse = parser.parse('gx')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[0].rule_name, 'position')
        self.assertEqual(parse[1].value, 'x')

        parse = parser.parse('gy')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[1].value, 'y')

        parse = parser.parse('g#')
        self.assertEqual(parse.rule_name, 'alteration')
        self.assertEqual(parse[1].value, '#')

    def test_alterationSuffixes(self):
        """Test suffixes on accidentals, which make no sense but sometimes occur"""
        gabc = "ix~fgfg"
        parser = ParserGABC(root='music')
        parse = parser.parse(gabc)
        self.assertEqual(parse.value, 'i | x | ~ | f | g | f | g')
    
    def test_polyphonicAlterations(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('f{ix}g')
        n1, polyphony, n2 = parse
        self.assertEqual(len(polyphony), 3)
        self.assertEqual(polyphony.rule_name, 'polyphony')
        self.assertEqual(polyphony[1].rule_name, 'alteration')

class TestText(unittest.TestCase):
    def test_text(self):
        parser = ParserGABC(root='text')
        parse = parser.parse('hello')
        self.assertTrue(parse.value, 'hello')
    
    def test_textWithSpaces(self):
        parser = ParserGABC(root='text')
        parse = parser.parse('hello world')
        self.assertTrue(parse.value, 'hello world')
    
    def test_textCannotStartWithSpace(self):
        parser = ParserGABC(root='text')
        test_fn = lambda: parser.parse(' hello')
        self.assertRaises(NoMatch, test_fn)

    def test_nonLyricsSpaces(self):
        parser = ParserGABC(root='body')
        for gabc in ["A(f) *(::)", "A(f) *(::)", "A(f) * (::)"]:
            parse = parser.parse(gabc)
            word1, _, bar, _ = parse
            text, _, pausa, _ = bar[0]
            self.assertEqual(text[0].rule_name, 'annotation')
            self.assertEqual(text[0].value, '*')

    def test_nonLyricTags(self):
        parser = ParserGABC(root='text')
        parse = parser.parse('<sp>V/</sp>.')
        self.assertEqual(parse[0].rule_name, 'annotation')
        self.assertEqual(parse[0].value, '<sp>V/</sp>.')

    def test_lyricTags(self):
        parser = ParserGABC(root='text')
        h, e, llo = parser.parse('H<i>e</i>llo')
        self.assertEqual(h.value, 'H')
        self.assertEqual(e.rule_name, 'tag')
        self.assertEqual(e.value, '<i> | e | </i>')
        self.assertEqual(llo.value, 'llo')
    
    def test_stars(self):
        parser = ParserGABC(root='star')
        examples = [
            ('*', '*'),
            ('**', '**'),
            ('<c>*</c>', '*'),
            ('<c>*</c>', '*'),
            ('<c>**</c>', '**')
        ]
        for example, value in examples:
            star = parser.parse(example)
            self.assertEqual(star.rule_name, 'star')
            if len(star) > 1:
                self.assertEqual(star[1].value, value)
            else:
                self.assertEqual(star[0].value, value)
        
    def test_repeats(self):
        parser = ParserGABC(root='annotation')
        examples = [
            '<i>i</i>',
            '<i>ii.</i>',
            '<i>iij.</i>',
            '<i>ij.</i>',
            '<i>Repeat :</i>',
            '<i>Repeat: </i>',
            '<i>Repeat:</i>',
            '<i>Repet.</i>',
            '<i>Repet</i>',
            '<i>Repetitur:</i>',
            '<i>Repetitur</i>',
            '<i>repeats :</i>',
        ]
        for example in examples:
            parse = parser.parse(example)
            (_, rep, _), = parse
            self.assertEqual(parse[0].rule_name, 'repeat')
            self.assertEqual(rep.value, example[3:-4])
    
    def test_psalm(self):
        parser = ParserGABC(root='annotation')
        examples = [
            '<i>Ps.</i>',
            '<i>Ps. 117.</i>',
            '<i>Ps. 117</i>',
            '<i>Ps. 50.</i>',
            '<i>Ps. 50</i>',
            '<i>Ps.~50.</i>'
        ]
        for example in examples:
            parse = parser.parse(example)
            (_, el, _), = parse
            self.assertEqual(parse[0].rule_name, 'psalm')
            self.assertEqual(el.value, example[3:-4])

    def test_TP(self):
        parser = ParserGABC(root='annotation')
        examples = [
            '<i>T. P. </i>',
            '<i>T. P.</i>',
            '<i>T.P.</i>',
            '<i>T.P</i>',
            '<i> T.P. </i>',
            '<i> T.P.</i>'
        ]
        for example in examples:
            parse = parser.parse(example)
            (_, el, _), = parse
            self.assertEqual(parse[0].rule_name, 'TP')
            self.assertEqual(el.value, example[3:-4])

    def test_latex(self):
        parser = ParserGABC(root='annotation')
        examples = [
            '<v>$\\star$</v>',
            '<v>\\\'y</v>',
            '<v>\\ae</v>',
            '<v>\\greheightstar</v>',
            '<v>\\gresixstar</v>'
        ]
        for example in examples:
            parse = parser.parse(example)
            (_, el, _), = parse
            self.assertEqual(parse[0].rule_name, 'latex')
            self.assertEqual(el.value, example[3:-4])

    def test_others(self):
        parser = ParserGABC(root='annotation')
        examples = [
            ('V', '<sp>V/</sp>',),
            ('V', '<sp>V/</sp>.'),
            ('V', '<sp>V/</sp>.'),
            ('R', '<sp>R/</sp>'),
            ('R', '<sp>R/</sp>.'),
            ('R', '<sp>R/</sp>.'),
            ('A', '<sp>A/</sp>'),
            ('A', '<sp>A/</sp>.'),
            ('A', '<sp>A/</sp>.'),
        ]
        for rule_name, example in examples:
            parse = parser.parse(example)
            self.assertEqual(parse[0].rule_name, rule_name)
            self.assertEqual(parse[0].value, example)