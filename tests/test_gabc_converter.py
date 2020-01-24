"""Unittests for the GABC to Volpiano converter

Todo:
    * Test conversion of example files
    * Test whether music can be empty
    * Test handling of accidentals at non-supported positions 
      (e.g. not b-flat or e-flat)
    * Test flat clefs
    * Test f2 clef
    * Test f1 clef?
"""
import unittest
import music21
from arpeggio import visit_parse_tree
from chant21 import Note
from chant21 import Neume
from chant21 import Syllable
from chant21 import Alteration
from chant21 import Comma
from chant21 import Barline
from chant21 import Clef
from chant21 import GABCParser
from chant21.gabc_converter import Visitor
from chant21.gabc_converter import gabcPositionToStep
from chant21.gabc_converter import MissingClef

class TestFile(unittest.TestCase):
    def test_file(self):
        parser = GABCParser(root='file')
        file_str = 'title:Title!;\nattr1:value1;%%\n\n(c2) a(f)b(g) c(h)\ni(j)'
        parse = parser.parse(file_str)
        chant = visit_parse_tree(parse, Visitor())

        self.assertEqual(chant.metadata.title, 'Title!')

        ed = chant.editorial
        self.assertEqual(ed.title, 'Title!')
        self.assertEqual(ed.attr1, 'value1')
        
        notes = chant.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'D')
        self.assertEqual(notes[2].name, 'E')
        self.assertEqual(notes[3].name, 'G')
        
    def test_header(self):
        parser = GABCParser(root='header')
        parse = parser.parse('attr1: value1;\nattr2:value2;')
        header = visit_parse_tree(parse, Visitor())
        target = dict(attr1='value1', attr2='value2')
        self.assertDictEqual(header, target)

class TestGABCPitchConversion(unittest.TestCase):
    def test_positions(self):
        self.assertEqual(gabcPositionToStep('c', 'c1'), 'B3')
        self.assertEqual(gabcPositionToStep('d', 'c1'), 'C4')
        self.assertEqual(gabcPositionToStep('e', 'c1'), 'D4')
        
        self.assertEqual(gabcPositionToStep('e', 'c2'), 'B3')
        self.assertEqual(gabcPositionToStep('f', 'c2'), 'C4')
        self.assertEqual(gabcPositionToStep('g', 'c2'), 'D4')
        self.assertEqual(gabcPositionToStep('h', 'c2'), 'E4')

        self.assertEqual(gabcPositionToStep('g', 'c3'), 'B4')
        self.assertEqual(gabcPositionToStep('h', 'c3'), 'C5')
        self.assertEqual(gabcPositionToStep('i', 'c3'), 'D5')

class TestAlterations(unittest.TestCase):
    def test_alterations(self):
        parser = GABCParser(root='alteration')
        for alteration in 'xy#':
            parse = parser.parse(f'f{alteration}')
            element = visit_parse_tree(parse, Visitor())
            ed = element.editorial
            self.assertIsInstance(element, Alteration)
            self.assertEqual(ed.gabcPosition, 'f')
            self.assertEqual(ed.gabcAlteration, alteration)

    def test_flats(self):
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) a(exee,e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[0].pitch.accidental.name, 'flat')
        self.assertEqual(notes[1].name, 'B-')
        self.assertEqual(notes[1].pitch.accidental.name, 'flat')
        self.assertEqual(notes[2].name, 'B')
        self.assertIsNone(notes[2].pitch.accidental)
    
    def test_naturals(self): 
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) a(eexeeyee,e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B')
        self.assertEqual(notes[1].name, 'B-')
        self.assertEqual(notes[2].name, 'B')
        self.assertEqual(notes[3].name, 'B')
        self.assertEqual(notes[4].name, 'B')

        self.assertIsNone(notes[0].pitch.accidental)
        self.assertEqual(notes[1].pitch.accidental.name, 'flat')
        self.assertEqual(notes[2].pitch.accidental.name, 'natural')
        self.assertEqual(notes[3].pitch.accidental.name, 'natural')
        self.assertIsNone(notes[4].pitch.accidental)

    def test_breath_mark(self):
        """Test whether breath marks reset the accidentals"""
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) (exe,fe)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[1].name, 'C')
        self.assertEqual(notes[2].name, 'B')

    def test_word_boundaries(self):
        """Test whether word boundaries reset accidentals"""
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) a(exfe) c(e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'B-')
        self.assertEqual(notes[2].name, 'B')
    
    def test_syllable_boundaries(self):
        """Test whether flats are NOT reset by syllable boundaries"""
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) a(exe)b(e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[1].name, 'B-')

    def test_flat_clefs(self):
        """Test whether flats are NOT reset by syllable boundaries"""
        parser = GABCParser(root='body')    
        parse = parser.parse('(cb2) (e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')

    def test_naturals_in_flat_clefs(self):
        """Test whether naturals work in flat clefs"""
        parser = GABCParser(root='body')    
        parse = parser.parse('(cb2) (eeyee,e) (e)')
        stream = visit_parse_tree(parse, Visitor())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[1].name, 'B')
        self.assertEqual(notes[1].pitch.accidental.name, 'natural')
        self.assertEqual(notes[2].name, 'B')
        self.assertEqual(notes[2].pitch.accidental.name, 'natural')
        self.assertEqual(notes[3].name, 'B-')
        self.assertEqual(notes[3].pitch.accidental.name, 'flat')
        self.assertEqual(notes[4].name, 'B-')
        self.assertEqual(notes[4].pitch.accidental.name, 'flat')

class TestText(unittest.TestCase):

    def test_text(self):
        parser = GABCParser(root='body')    
        parse = parser.parse('a(c2) word(e)1(f) word2(g)')
        chant = visit_parse_tree(parse, Visitor())
        clef, word1, word2 = chant.recurse(classFilter='ChantElement')
        self.assertEqual(clef.text, 'a')
        self.assertEqual(word1.text, 'word1')
        self.assertEqual(word2.text, 'word2')

        syll1, syll2 = word1.elements
        self.assertEqual(syll1.text, 'word')
        self.assertEqual(syll2.text, '1')
        self.assertEqual(syll1.flat.notes[0].lyric, 'word')
        self.assertEqual(syll2.flat.notes[0].lyric, '1')

    def test_textAfterAccidental(self):
        parser = GABCParser(root='body')    
        parse = parser.parse('(c2) bla(eye)')
        chant = visit_parse_tree(parse, Visitor())
        clef, word = chant.recurse(classFilter='ChantElement')
        self.assertIsNone(clef.text)
        self.assertEqual(word.text, 'bla')
        note = word.flat.notes[0]
        self.assertEqual(note.lyric, 'bla')
    
    def test_singleSyllable(self):
        parser = GABCParser(root='word')    
        parse = parser.parse('s1(f)')
        word = visit_parse_tree(parse, Visitor())
        s1, = word.syllables
        self.assertEqual(s1.lyrics[0].syllabic, 'single')

    def test_twoSyllables(self):
        parser = GABCParser(root='word')    
        parse = parser.parse('s1(f)s2(f)')
        word = visit_parse_tree(parse, Visitor())
        s1, s2 = word.syllables
        self.assertEqual(s1.lyrics[0].syllabic, 'begin')
        self.assertEqual(s2.lyrics[0].syllabic, 'end')

    def test_threeOrMoreSyllables(self):
        parser = GABCParser(root='word')    
        parse = parser.parse('s1(f)s2(f)s3(g)s4(f)')
        word = visit_parse_tree(parse, Visitor())
        s1, s2, s3, s4 = word.syllables
        self.assertEqual(s1.lyrics[0].syllabic, 'begin')
        self.assertEqual(s2.lyrics[0].syllabic, 'middle')
        self.assertEqual(s3.lyrics[0].syllabic, 'middle')
        self.assertEqual(s4.lyrics[0].syllabic, 'end')

class TestBarClefs(unittest.TestCase):
    def test_bar(self):
        parser = GABCParser(root='bar_or_clef')
        for barline in [':', '::', ';1', ';2', ';3', ':?']:
            parse = parser.parse(f'a({barline})')
            bar = visit_parse_tree(parse, Visitor())
            self.assertIsInstance(bar, Barline)
            self.assertEqual(bar.text, 'a')
            self.assertEqual(bar.editorial.gabc, barline)

    def test_clefs(self):
        parser = GABCParser(root='clef')
        for clef in ['c1', 'c2', 'c3', 'c4', 'f3', 'f4', 'cb3', 'cb4']:
            parse = parser.parse(clef)
            element = visit_parse_tree(parse, Visitor())
            self.assertIsInstance(element, music21.clef.TrebleClef)
            self.assertEqual(element.editorial.gabc, clef)

    def test_missing_clef(self):
        parser = GABCParser(root='body')
        parse = parser.parse('a(fgf)')
        test_fn = lambda: visit_parse_tree(parse, Visitor())
        self.assertRaises(MissingClef, test_fn)
        
class TestSyllables(unittest.TestCase):
    def test_syllable(self):
        parser = GABCParser(root='syllable')
        parse = parser.parse('A(fg)')
        syllable = visit_parse_tree(parse, Visitor())
        self.assertEqual(syllable.text, 'A')
        self.assertEqual(len(syllable.flat.notes), 2)
        self.assertEqual(len(syllable), 1)

    def test_multipleNeumes(self):
        parser = GABCParser(root='syllable')
        parse = parser.parse('A(fg/fg)')
        syllable = visit_parse_tree(parse, Visitor())
        self.assertEqual(syllable.text, 'A')
        self.assertEqual(len(syllable.flat.notes), 4)
        self.assertEqual(len(syllable), 2)
        
    def test_syllablesWithCommas(self):
        parser = GABCParser(root='word')    
        gabc = 'a(f)(,)(f)b(f)'
        parse = parser.parse(gabc)
        word = visit_parse_tree(parse, Visitor())
        self.assertEqual(len(word), 2)
        self.assertIsInstance(word[0][1], Comma)
        self.assertEqual(len(word.flat.notes), 3)
    
class TestNeumes(unittest.TestCase):

    def test_singleNeume(self):
        parser = GABCParser(root='music')
        parse = parser.parse('fgf')
        elements = visit_parse_tree(parse, Visitor())
        self.assertEqual(len(elements), 1)
        
        neume = elements[0]
        self.assertEqual(len(neume), 3)
        self.assertIsInstance(neume[0], music21.note.Note)
        self.assertIsInstance(neume[1], music21.note.Note)
        self.assertIsInstance(neume[2], music21.note.Note)
        self.assertEqual(neume[0].editorial.gabcPosition, 'f')
        self.assertEqual(neume[1].editorial.gabcPosition, 'g')
        self.assertEqual(neume[2].editorial.gabcPosition, 'f')

    def test_multipleNeumes(self):
        parser = GABCParser(root='music')
        parse = parser.parse('eh/hi')
        elements = visit_parse_tree(parse, Visitor())
        self.assertEqual(len(elements), 2)
        self.assertIsInstance(elements[0], Neume)
        self.assertEqual(len(elements[0]), 2)
        self.assertIsInstance(elements[1], Neume)
        self.assertEqual(len(elements[1]), 2)

    def test_articulationBeforeComma(self):
        parser = GABCParser(root='music')
        parse = parser.parse("fgf,g")
        elements = visit_parse_tree(parse, Visitor())
        self.assertEqual(len(elements), 3)
        self.assertIsInstance(elements[0], Neume)
        self.assertIsInstance(elements[1], Comma)
        self.assertIsInstance(elements[2], Neume)
        note = elements[0][-1]
        self.assertEqual(len(note.articulations), 1)
        self.assertIsInstance(note.articulations[0], music21.articulations.BreathMark)
        self.assertIsInstance(note.articulations[0], Comma)
    
class TestNotes(unittest.TestCase):
    
    def test_note_suffixes(self):
        parser = GABCParser(root='note')
        parse = parser.parse('fs<.')
        note = visit_parse_tree(parse, Visitor())
        ed = note.editorial
        self.assertEqual(ed.gabcPosition, 'f')
        self.assertEqual(ed.gabcShape, 's<')
        self.assertEqual(ed.gabcRhythmicSign, '.')
    
    def test_note_prefix(self):
        parser = GABCParser(root='note')
        parse = parser.parse(f'-f')
        note = visit_parse_tree(parse, Visitor())
        ed = note.editorial
        self.assertEqual(ed.gabcPosition, 'f')
        self.assertEqual(ed.gabcPrefix, '-')
        self.assertTrue(ed.liquescence)

    def test_positions(self):
        parser = GABCParser(root='position')
        for position in 'abcdefghijklmABCDEFGHIJKLM':
            parse = parser.parse(position)
            output = visit_parse_tree(parse, Visitor())
            self.assertEqual(output, position)

if __name__ == '__main__':
    unittest.main()