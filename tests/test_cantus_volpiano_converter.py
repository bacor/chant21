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

    def test_chant(self):
        parser = ParserCantusVolpiano(root='chant')
        parse = parser.parser.parse('1---fg-h--f--g---f')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(chant, Chant)
        self.assertEqual(len(chant), 3)
        self.assertIsInstance(chant[0], Clef)

    def test_volpiano(self):
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---fg-h--f--g---f')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        self.assertIsInstance(chant, Chant)
        self.assertEqual(len(chant), 3)
        self.assertIsInstance(chant[0], Clef)

class TestVolpiano(unittest.TestCase):
    def test_b_flats(self):
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---j--ij--j---j-h-j---4')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 6)
        self.assertEqual(notes[0].nameWithOctave, 'B4')
        self.assertEqual(notes[1].nameWithOctave, 'B-4')
        self.assertEqual(notes[2].nameWithOctave, 'B-4')
        self.assertEqual(notes[3].nameWithOctave, 'B4')
        self.assertEqual(notes[4].nameWithOctave, 'A4')
        self.assertEqual(notes[5].nameWithOctave, 'B4')

    def test_other_b_flats(self):
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---b--yb--b---b-a-b---4')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 6)
        self.assertEqual(notes[0].nameWithOctave, 'B3')
        self.assertEqual(notes[1].nameWithOctave, 'B-3')
        self.assertEqual(notes[2].nameWithOctave, 'B-3')
        self.assertEqual(notes[3].nameWithOctave, 'B3')
        self.assertEqual(notes[4].nameWithOctave, 'A3')
        self.assertEqual(notes[5].nameWithOctave, 'B3')

    def test_e_flats(self):
        parser = ParserCantusVolpiano(root='volpiano')
        parse = parser.parser.parse('1---e--we--e--We--e---4')
        chant = visitParseTree(parse, VisitorCantusVolpiano())
        notes = chant.recurse().notes
        self.assertEqual(len(notes), 5)
        self.assertEqual(notes[0].nameWithOctave, 'E4')
        self.assertEqual(notes[1].nameWithOctave, 'E-4')
        self.assertEqual(notes[2].nameWithOctave, 'E-4')
        self.assertEqual(notes[3].nameWithOctave, 'E4')
        self.assertEqual(notes[4].nameWithOctave, 'E4')
        
class TestVolpianoPositionConverter(unittest.TestCase):
    def test_g_clef(self):
        self.assertEqual(volpianoPositionToStep('8', clef='g'), 'F4')
        self.assertEqual(volpianoPositionToStep('9', clef='g'), 'G4')
        self.assertEqual(volpianoPositionToStep('a', clef='g'), 'A4')
        self.assertEqual(volpianoPositionToStep('b', clef='g'), 'B4')
        self.assertEqual(volpianoPositionToStep('c', clef='g'), 'C5')
        self.assertEqual(volpianoPositionToStep('d', clef='g'), 'D5')
        self.assertEqual(volpianoPositionToStep('e', clef='g'), 'E5')
        self.assertEqual(volpianoPositionToStep('f', clef='g'), 'F5')
        self.assertEqual(volpianoPositionToStep('g', clef='g'), 'G5')
        self.assertEqual(volpianoPositionToStep('h', clef='g'), 'A5')
        self.assertEqual(volpianoPositionToStep('j', clef='g'), 'B5')
        self.assertEqual(volpianoPositionToStep('k', clef='g'), 'C6')
        self.assertEqual(volpianoPositionToStep('l', clef='g'), 'D6')
        self.assertEqual(volpianoPositionToStep('m', clef='g'), 'E6')
        self.assertEqual(volpianoPositionToStep('n', clef='g'), 'F6')
        self.assertEqual(volpianoPositionToStep('o', clef='g'), 'G6')
        self.assertEqual(volpianoPositionToStep('p', clef='g'), 'A6')
        self.assertEqual(volpianoPositionToStep('q', clef='g'), 'B6')
        self.assertEqual(volpianoPositionToStep('r', clef='g'), 'C7')
        self.assertEqual(volpianoPositionToStep('s', clef='g'), 'D7')

    def test_f_clef(self):
        self.assertEqual(volpianoPositionToStep('8', clef='f'), 'A2')
        self.assertEqual(volpianoPositionToStep('9', clef='f'), 'B2')
        self.assertEqual(volpianoPositionToStep('a', clef='f'), 'C3')
        self.assertEqual(volpianoPositionToStep('b', clef='f'), 'D3')
        self.assertEqual(volpianoPositionToStep('c', clef='f'), 'E3')
        self.assertEqual(volpianoPositionToStep('d', clef='f'), 'F3')
        self.assertEqual(volpianoPositionToStep('e', clef='f'), 'G3')
        self.assertEqual(volpianoPositionToStep('f', clef='f'), 'A3')
        self.assertEqual(volpianoPositionToStep('g', clef='f'), 'B3')
        self.assertEqual(volpianoPositionToStep('h', clef='f'), 'C4')
        self.assertEqual(volpianoPositionToStep('j', clef='f'), 'D4')
        self.assertEqual(volpianoPositionToStep('k', clef='f'), 'E4')
        self.assertEqual(volpianoPositionToStep('l', clef='f'), 'F4')
        self.assertEqual(volpianoPositionToStep('m', clef='f'), 'G4')
        self.assertEqual(volpianoPositionToStep('n', clef='f'), 'A4')
        self.assertEqual(volpianoPositionToStep('o', clef='f'), 'B4')
        self.assertEqual(volpianoPositionToStep('p', clef='f'), 'C5')
        self.assertEqual(volpianoPositionToStep('q', clef='f'), 'D5')
        self.assertEqual(volpianoPositionToStep('r', clef='f'), 'E5')
        self.assertEqual(volpianoPositionToStep('s', clef='f'), 'F5')

class TestConverter(unittest.TestCase):
    def test_converter(self):
        chant = converter.parse('1---f-g---4', format='Cantus')
        self.assertIsInstance(chant, Chant)