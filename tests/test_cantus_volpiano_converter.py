import unittest
from arpeggio import visit_parse_tree as visitParseTree
from music21 import converter

from chant21 import Chant
from chant21 import Note
from chant21 import Section
from chant21 import Neume
from chant21 import Syllable
from chant21 import Word
from chant21 import Alteration
from chant21 import Flat
from chant21 import Natural
from chant21 import Clef
from chant21 import ParserGABC
from chant21 import Pausa
from chant21 import PausaMinima
from chant21 import PausaMinor
from chant21 import PausaMajor
from chant21 import PausaFinalis

from chant21 import LineBreak
from chant21 import ColumnBreak
from chant21 import PageBreak

from chant21 import ParserCantusVolpiano
from chant21.converter_cantus_volpiano import VisitorCantusVolpiano
from chant21.converter_cantus_volpiano import volpianoPositionToStep
from chant21.converter_cantus_volpiano import TextAlignmentError
from chant21.converter_cantus_volpiano import SyllableAlignmentError
from chant21.converter_cantus_volpiano import WordAlignmentError
from chant21.converter_cantus_volpiano import SectionAlignmentError

class TestElements(unittest.TestCase):
    def test_note(self):
        parser = ParserCantusVolpiano(root='note')
        parse = parser.parser.parse('f')
        note = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(note, Note)
        self.assertEqual(note.editorial.volpianoPosition, 'f')

    def test_liquescent(self):
        parser = ParserCantusVolpiano(root='liquescent')
        parse = parser.parser.parse('F')
        note = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(note, Note)
        self.assertEqual(note.editorial.volpianoPosition, 'f')
        self.assertEqual(note.editorial.liquescence, True)
        self.assertEqual(note.notehead, 'x')
    
    def test_g_clef(self):
        parser = ParserCantusVolpiano(root='clef')
        parse = parser.parser.parse('1')
        clef = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(clef, Clef)
        self.assertEqual(clef.editorial.volpiano, '1')
    
    def test_f_clef(self):
        # TODO not really supported yet
        parser = ParserCantusVolpiano(root='clef')
        parse = parser.parser.parse('2')
        clef = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(clef, Clef)
        self.assertEqual(clef.editorial.volpiano, '2')
    
    def test_line_break(self):
        parser = ParserCantusVolpiano(root='break')
        parse = parser.parser.parse('7')
        brk = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(brk, LineBreak)

    def test_column_break(self):
        parser = ParserCantusVolpiano(root='break')
        parse = parser.parser.parse('777')
        brk = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(brk, ColumnBreak)

    def test_page_break(self):
        parser = ParserCantusVolpiano(root='break')
        parse = parser.parser.parse('77')
        brk = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(brk, PageBreak)

    def test_flats(self):
        parser = ParserCantusVolpiano(root='alteration')
        parse = parser.parser.parse('i')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Alteration)
        self.assertIsInstance(alteration, Flat)
        self.assertEqual(alteration.editorial.volpiano, 'i')
        self.assertEqual(alteration.editorial.volpianoPosition, 'j')

        # High e flat 
        parse = parser.parser.parse('x')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Flat)
        self.assertEqual(alteration.editorial.volpianoPosition, 'm')

        # Low e flat
        parse = parser.parser.parse('w')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Flat)
        self.assertEqual(alteration.editorial.volpianoPosition, 'e')

        # Low b flat
        parse = parser.parser.parse('y')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Flat)
        self.assertEqual(alteration.editorial.volpianoPosition, 'b')

        # High b flat
        parse = parser.parser.parse('z')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Flat)
        self.assertEqual(alteration.editorial.volpianoPosition, 'q')

    def test_naturals(self):
        parser = ParserCantusVolpiano(root='alteration')
        parse = parser.parser.parse('I')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Alteration)
        self.assertIsInstance(alteration, Natural)
        self.assertEqual(alteration.editorial.volpiano, 'I')
        self.assertEqual(alteration.editorial.volpianoPosition, 'j')

        # High e flat 
        parse = parser.parser.parse('X')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Natural)
        self.assertEqual(alteration.editorial.volpianoPosition, 'm')

        # Low e flat
        parse = parser.parser.parse('W')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Natural)
        self.assertEqual(alteration.editorial.volpianoPosition, 'e')

        # Low b flat
        parse = parser.parser.parse('Y')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Natural)
        self.assertEqual(alteration.editorial.volpianoPosition, 'b')

        # High b flat
        parse = parser.parser.parse('Z')
        alteration = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(alteration, Natural)
        self.assertEqual(alteration.editorial.volpianoPosition, 'q')

    def test_chant_end(self):
        parser = ParserCantusVolpiano(root='chant_end')
        parse = parser.parser.parse('4')
        bar = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(bar, PausaFinalis)

    def test_section_end(self):
        parser = ParserCantusVolpiano(root='section_end')
        parse = parser.parser.parse('3')
        bar = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(bar, PausaMajor)

    def test_neume(self):
        parser = ParserCantusVolpiano(root='neume')
        parse = parser.parser.parse('fg')
        neume = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(neume, Neume)
        self.assertEqual(len(neume), 2)
        self.assertIsInstance(neume[0], Note)

    def test_syllable(self):
        parser = ParserCantusVolpiano(root='syllable')
        parse = parser.parser.parse('fg-h-g')
        syll = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(syll, Syllable)
        self.assertEqual(len(syll), 3)
        self.assertIsInstance(syll[0], Neume)
    
    def test_word(self):
        parser = ParserCantusVolpiano(root='word')
        parse = parser.parser.parse('fg-h--f--g')
        word = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(word, Word)
        self.assertEqual(len(word), 3)
        self.assertIsInstance(word[0], Syllable)

    def test_volpiano(self):
        """Test the basic structure of a chant: division in sections, words
        and syllables"""
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---fg-h--f--g---f')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(chant, Chant)
        self.assertIsInstance(chant[0], Section)
        (word1, word2, word3), = chant
        self.assertIsInstance(word1, Word)
        self.assertIsInstance(word1[0], Syllable)
        self.assertIsInstance(word1[0][0], Clef)

class TestVolpianoPositionConverter(unittest.TestCase):
    def test_g_clef(self):
        self.assertEqual(volpianoPositionToStep('8', clef='g'), 'F3')
        self.assertEqual(volpianoPositionToStep('9', clef='g'), 'G3')
        self.assertEqual(volpianoPositionToStep('a', clef='g'), 'A3')
        self.assertEqual(volpianoPositionToStep('b', clef='g'), 'B3')
        self.assertEqual(volpianoPositionToStep('c', clef='g'), 'C4')
        self.assertEqual(volpianoPositionToStep('d', clef='g'), 'D4')
        self.assertEqual(volpianoPositionToStep('e', clef='g'), 'E4')
        self.assertEqual(volpianoPositionToStep('f', clef='g'), 'F4')
        self.assertEqual(volpianoPositionToStep('g', clef='g'), 'G4')
        self.assertEqual(volpianoPositionToStep('h', clef='g'), 'A4')
        self.assertEqual(volpianoPositionToStep('j', clef='g'), 'B4')
        self.assertEqual(volpianoPositionToStep('k', clef='g'), 'C5')
        self.assertEqual(volpianoPositionToStep('l', clef='g'), 'D5')
        self.assertEqual(volpianoPositionToStep('m', clef='g'), 'E5')
        self.assertEqual(volpianoPositionToStep('n', clef='g'), 'F5')
        self.assertEqual(volpianoPositionToStep('o', clef='g'), 'G5')
        self.assertEqual(volpianoPositionToStep('p', clef='g'), 'A5')
        self.assertEqual(volpianoPositionToStep('q', clef='g'), 'B5')
        self.assertEqual(volpianoPositionToStep('r', clef='g'), 'C6')
        self.assertEqual(volpianoPositionToStep('s', clef='g'), 'D6')

    def test_f_clef(self):
        self.assertEqual(volpianoPositionToStep('8', clef='f'), 'A1')
        self.assertEqual(volpianoPositionToStep('9', clef='f'), 'B1')
        self.assertEqual(volpianoPositionToStep('a', clef='f'), 'C2')
        self.assertEqual(volpianoPositionToStep('b', clef='f'), 'D2')
        self.assertEqual(volpianoPositionToStep('c', clef='f'), 'E2')
        self.assertEqual(volpianoPositionToStep('d', clef='f'), 'F2')
        self.assertEqual(volpianoPositionToStep('e', clef='f'), 'G2')
        self.assertEqual(volpianoPositionToStep('f', clef='f'), 'A2')
        self.assertEqual(volpianoPositionToStep('g', clef='f'), 'B2')
        self.assertEqual(volpianoPositionToStep('h', clef='f'), 'C3')
        self.assertEqual(volpianoPositionToStep('j', clef='f'), 'D3')
        self.assertEqual(volpianoPositionToStep('k', clef='f'), 'E3')
        self.assertEqual(volpianoPositionToStep('l', clef='f'), 'F3')
        self.assertEqual(volpianoPositionToStep('m', clef='f'), 'G3')
        self.assertEqual(volpianoPositionToStep('n', clef='f'), 'A3')
        self.assertEqual(volpianoPositionToStep('o', clef='f'), 'B3')
        self.assertEqual(volpianoPositionToStep('p', clef='f'), 'C4')
        self.assertEqual(volpianoPositionToStep('q', clef='f'), 'D4')
        self.assertEqual(volpianoPositionToStep('r', clef='f'), 'E4')
        self.assertEqual(volpianoPositionToStep('s', clef='f'), 'F4')

class TestConverter(unittest.TestCase):
    def test_converter(self):
        chant = converter.parse('1---f-g---4', format='Cantus')
        self.assertIsInstance(chant, Chant)

    def test_b_flats(self):
        chant = converter.parse('1---j--ij--j---j-h-j---4', format='cantus')
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 6)
        self.assertEqual(notes[0].nameWithOctave, 'B4')
        self.assertEqual(notes[1].nameWithOctave, 'B-4')
        self.assertEqual(notes[2].nameWithOctave, 'B-4')
        self.assertEqual(notes[3].nameWithOctave, 'B4')
        self.assertEqual(notes[4].nameWithOctave, 'A4')
        self.assertEqual(notes[5].nameWithOctave, 'B4')

    def test_other_b_flats(self):
        chant = converter.parse('1---b--yb--b---b-a-b---4', format='cantus')
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 6)
        self.assertEqual(notes[0].nameWithOctave, 'B3')
        self.assertEqual(notes[1].nameWithOctave, 'B-3')
        self.assertEqual(notes[2].nameWithOctave, 'B-3')
        self.assertEqual(notes[3].nameWithOctave, 'B3')
        self.assertEqual(notes[4].nameWithOctave, 'A3')
        self.assertEqual(notes[5].nameWithOctave, 'B3')

    def test_e_flats(self):
        chant = converter.parse('1---e--we--e--We--e---4', format='cantus')
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 5)
        self.assertEqual(notes[0].nameWithOctave, 'E4')
        self.assertEqual(notes[1].nameWithOctave, 'E-4')
        self.assertEqual(notes[2].nameWithOctave, 'E-4')
        self.assertEqual(notes[3].nameWithOctave, 'E4')
        self.assertEqual(notes[4].nameWithOctave, 'E4')
        
    def test_sections(self):
        ch = converter.parse('1---fg-h---3---f-g---4', format='cantus')
        self.assertEqual(len(ch), 2)
        sect1, sect2 = ch
        self.assertIsInstance(sect1, Section)
        self.assertIsInstance(sect2, Section)

    def test_clef(self):
        section, = converter.parse('1---fg---4', format='cantus')
        self.assertIsInstance(section[0], Word)
        self.assertIsInstance(section[0][0], Syllable)
        self.assertIsInstance(section[0][0][0], Clef)

    def test_alternative_hyphenation(self):
        volpiano = '1--f--fg-g--f'
        chant = converter.parse(volpiano, format='cantus')
        self.assertEqual(len(chant[0]), 4)
        word1, word2, word3, word4 = chant[0]
        self.assertIsInstance(word1, Word)
        self.assertIsInstance(word2, Word)
        self.assertIsInstance(word3, Word)
        self.assertIsInstance(word4, Word)
        self.assertEqual(len(word3), 2)
        self.assertIsInstance(word3[0], Syllable)
        self.assertIsInstance(word3[1], Syllable)
        
class TestVolpianoAndTextConversion(unittest.TestCase):

    def test_volpiano_and_text(self):
        ch = converter.parse('1---f--g---f---3---f---4/Amen et | A', format='cantus')
        # print(ch)
        self.assertTrue(True)

    def test_hyphens(self):
        ch = converter.parse('1---a---cde--d--d---4/A facie', format='cantus')
        self.assertEqual(ch[0][1][0].lyric, 'a')
        self.assertEqual(ch[0][2][0].lyric, 'fa')
        self.assertEqual(ch[0][2][1].lyric, 'ci')
        self.assertEqual(ch[0][2][2].lyric, 'e')

    def test_pitchless_text(self):
        input_str = ('1---df---efd--c---4---c--d--f--f---3---f--f--f--e--c--d7---3'
                     '/A fructu  | ~Cum invocarem | euouae')
        ch = converter.parse(input_str, format='cantus')
        self.assertEqual(len(ch), 3)
        self.assertEqual(ch[1][0][0].lyric.text, '~Cum invocarem')
    
    def test_misalignment_syllables(self):
        """Test the handling of misaligned syllables in the text and music. In 
        strict mode exceptions should be raised, otherwise the misalignment
        should be marked in the editorial information"""
        more_sylls_in_mus = ('1---a--b--c---d---3/bada ca')
        more_sylls_in_txt = ('1---a---d---3/bada ca')
        
        # Strict
        test_fn = lambda: converter.parse(more_sylls_in_mus, format='cantus-strict')
        self.assertRaises(SyllableAlignmentError, test_fn)
        test_fn = lambda: converter.parse(more_sylls_in_txt, format='cantus-strict')
        self.assertRaises(SyllableAlignmentError, test_fn)
        
        # Non-strict
        ch = converter.parse(more_sylls_in_mus, format='cantus')
        self.assertTrue(ch[0][1].editorial.misaligned)
        ch = converter.parse(more_sylls_in_txt, format='cantus')
        self.assertTrue(ch[0][1].editorial.misaligned)

    def test_misalignment_words(self):
        """Test the handling of misaligned words in the text and music. In 
        strict mode exceptions should be raised, otherwise the misalignment
        should be marked in the editorial information"""
        more_words_in_mus = ('1---a--b---d---e---3/bada ca')
        more_words_in_txt = ('1---a--b---d---3/bada ca da')
        
        # Strict
        test_fn = lambda: converter.parse(more_words_in_mus, format='cantus-strict')
        self.assertRaises(WordAlignmentError, test_fn)
        test_fn = lambda: converter.parse(more_words_in_txt, format='cantus-strict')
        self.assertRaises(WordAlignmentError, test_fn)

        # Non-strict
        ch = converter.parse(more_words_in_mus, format='cantus')
        self.assertTrue(ch[0].editorial.misaligned)
        ch = converter.parse(more_words_in_txt, format='cantus')
        self.assertTrue(ch[0].editorial.misaligned)

    def test_misalignment_sections(self):
        """Test the handling of misaligned sections in the text and music. In 
        strict mode exceptions should be raised, otherwise the misalignment
        should be marked in the editorial information"""
        more_secs_in_mus = ('1---a---b---3---c---3/ba ca da')
        more_secs_in_txt = ('1---a---b---c---3/ba ca | da')

        # Strict
        test_fn = lambda: converter.parse(more_secs_in_mus, format='cantus-strict')
        self.assertRaises(SectionAlignmentError, test_fn)
        test_fn = lambda: converter.parse(more_secs_in_txt, format='cantus-strict')
        self.assertRaises(SectionAlignmentError, test_fn)

        # Non-strict
        ch = converter.parse(more_secs_in_mus, format='cantus')
        self.assertTrue(ch.editorial.misaligned)
        ch = converter.parse(more_secs_in_txt, format='cantus')
        self.assertTrue(ch.editorial.misaligned)