"""Unittests for the GABC to Volpiano converter

Todo:
    * Test conversion of example files
"""
import unittest
from arpeggio import visit_parse_tree
from pygabc.parser import GABCParser
from pygabc.converter import *

class TestPositionToMidiConversion(unittest.TestCase):

    def test_clef_c1(self):
        tests = [
            ('a', 55), # G
            ('b', 57), # A
            ('c', 59), # B
            ('d', 60), # C
            ('e', 62), # D
            ('f', 64), # E
            ('g', 65), # F
            ('h', 67), # G
            ('i', 69), # A
            ('j', 71), # B
            ('k', 72), # C
            ('l', 74), # D
            ('m', 76), # E
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'c1', C=60)
            self.assertEqual(midi, target)        

    def test_clef_c2(self):
        tests = [
            ('a', 52), # E
            ('b', 53), # F
            ('c', 55), # G
            ('d', 57), # A
            ('e', 59), # B
            ('f', 60), # C
            ('g', 62), # D
            ('h', 64), # E
            ('i', 65), # F
            ('j', 67), # G
            ('k', 69), # A
            ('l', 71), # B
            ('m', 72), # C
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'c2', C=60)
            self.assertEqual(midi, target)

    def test_clef_c3(self):
        tests = [
            ('a', 48), # C
            ('b', 50), # D
            ('c', 52), # E
            ('d', 53), # F
            ('e', 55), # G
            ('f', 57), # A
            ('g', 59), # B
            ('h', 60), # C
            ('i', 62), # D
            ('j', 64), # E
            ('k', 65), # F
            ('l', 67), # G
            ('m', 69), # A
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'c3', C=60)
            self.assertEqual(midi, target)

    def test_clef_c4(self):
        tests = [
            ('a', 45), # A
            ('b', 47), # B
            ('c', 48), # C
            ('d', 50), # D
            ('e', 52), # E
            ('f', 53), # F
            ('g', 55), # G
            ('h', 57), # A
            ('i', 59), # B
            ('j', 60), # C
            ('k', 62), # D
            ('l', 64), # E
            ('m', 65), # F
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'c4', C=60)
            self.assertEqual(midi, target)

    def test_clef_f3(self):
        tests = [
            ('a', 53), # F
            ('b', 55), # G
            ('c', 57), # A
            ('d', 59), # B
            ('e', 60), # C
            ('f', 62), # D
            ('g', 64), # E
            ('h', 65), # F
            ('i', 67), # G
            ('j', 69), # A
            ('k', 71), # B
            ('l', 72), # C
            ('m', 74), # D
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'f3', C=60)
            self.assertEqual(midi, target)

    def test_clef_f4(self):
        tests = [
            ('a', 50), # D
            ('b', 52), # E
            ('c', 53), # F
            ('d', 55), # G
            ('e', 57), # A
            ('f', 59), # B
            ('g', 60), # C
            ('h', 62), # D
            ('i', 64), # E
            ('j', 65), # F
            ('k', 67), # G
            ('l', 69), # A
            ('m', 71), # B
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'f4', C=60)
            self.assertEqual(midi, target)

    def test_clef_cb3(self):
        tests = [
            ('a', 48), # C
            ('b', 50), # D
            ('c', 52), # E
            ('d', 53), # F
            ('e', 55), # G
            ('f', 57), # A
            ('g', 58), # B-flat
            ('h', 60), # C
            ('i', 62), # D
            ('j', 64), # E
            ('k', 65), # F
            ('l', 67), # G
            ('m', 69), # A
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'cb3', C=60)
            self.assertEqual(midi, target)

    def test_clef_cb4(self):
        tests = [
            ('a', 45), # A
            ('b', 46), # B-flat
            ('c', 48), # C
            ('d', 50), # D
            ('e', 52), # E
            ('f', 53), # F
            ('g', 55), # G
            ('h', 57), # A
            ('i', 58), # B-flat
            ('j', 60), # C
            ('k', 62), # D
            ('l', 64), # E
            ('m', 65), # F
        ]
        for position, target in tests:
            midi = position_to_midi(position, 'cb4', C=60)
            self.assertEqual(midi, target)

    def test_other_central_c(self):
        tests = [
            ('a', 55), # G
            ('b', 57), # A
            ('c', 59), # B
            ('d', 60), # C
            ('e', 62), # D
            ('f', 64), # E
            ('g', 65), # F
            ('h', 67), # G
            ('i', 69), # A
            ('j', 71), # B
            ('k', 72), # C
            ('l', 74), # D
            ('m', 76), # E
        ]
        for transposition in range(-1, 10):
            for position, target in tests:
                midi = position_to_midi(position, 'c1', C=60 + transposition)
                self.assertEqual(midi, target + transposition)

class TestConversionVisitor(unittest.TestCase):
    
    def test_syllable(self):
        parser = GABCParser(root='syllable')
        parse = parser.parse('A(fg)')
        text_music = visit_parse_tree(parse, VolpianoConverterVisitor())
        self.assertEqual(len(text_music), 2)
        text, music = text_music
        self.assertEqual(text, 'A')
        self.assertEqual(len(music), 2)
        self.assertEqual(music[0]['position'], 'f')
        self.assertEqual(music[1]['position'], 'g')

    def test_positions(self):
        parser = GABCParser(root='position')
        for position in 'abcdefghijklmABCDEFGHIJKLM':
            parse = parser.parse(position)
            output = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(output, position.lower())

    def test_clefs(self):
        parser = GABCParser(root='music')
        for clef in ['c1', 'c2', 'c3', 'c4', 'f3', 'f4', 'cb3', 'cb4']:
            parse = parser.parse(clef)
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'clef')
            self.assertEqual(events[0]['value'], clef)

    def test_barlines(self):
        parser = GABCParser(root='music')
        for gabc, target in BARLINES.items():
            parse = parser.parse(gabc)
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'barline')
            self.assertEqual(events[0]['value'], target)

    def test_spacers(self):
        parser = GABCParser(root='music')
        for gabc, target in SPACERS.items():
            parse = parser.parse(gabc)
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'spacer')
            self.assertEqual(events[0]['value'], target)

    def test_liquescent_neume_shapes(self):
        parser = GABCParser(root='music')
        for shape in LIQUESCENT_NEUME_SHAPES.keys():
            parse = parser.parse(f'f{shape}')
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'liquescent')
            self.assertEqual(events[0]['position'], 'f')

    def test_liquescent_prefix(self):
        parser = GABCParser(root='music')
        for prefix in LIQUESCENT_PREFIXES.keys():
            parse = parser.parse(f'{prefix}f')
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'liquescent')
            self.assertEqual(events[0]['position'], 'f')

    def test_alteration(self):
        parser = GABCParser(root='music') 
        for alteration, name in ALTERATIONS.items():
            parse = parser.parse(f'f{alteration}')
            events = visit_parse_tree(parse, VolpianoConverterVisitor())
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['type'], 'alteration')
            self.assertEqual(events[0]['position'], 'f')
            self.assertEqual(events[0]['value'], name)

class TestConversion(unittest.TestCase):
    
    def test_converter(self):
        converter = VolpianoConverter()
        text, volpiano = converter.convert('(c3) A(fgf)B(g) C(h)')
        self.assertEqual(text, ' A-B C')
        self.assertEqual(volpiano, '1---aba--b---c')

    def test_missing_clef(self):
        converter = VolpianoConverter()
        test_fn = lambda: converter.convert('A(fgf)')
        self.assertRaises(MissingClef, test_fn)

    def test_liquescents(self):
        converter = VolpianoConverter()
        text, music = converter.convert('(c2) (-fgfw)')
        self.assertEqual(music, '1---CdC')

    def test_notes(self):
        converter = VolpianoConverter()
        text, music = converter.convert('(c2) (fghij)')
        self.assertEqual(music, '1---cdefg')

    def test_word_boundaries(self):
        converter = VolpianoConverter()
        text, music = converter.convert('(c2) A(f) B(g)')
        self.assertEqual(music, f'1{MUSIC_WORD_BOUNDARY}c{MUSIC_WORD_BOUNDARY}d')
        self.assertEqual(text, f'{TEXT_WORD_BOUNDARY}A{TEXT_WORD_BOUNDARY}B')

    def test_syllable_boundaries(self):
        converter = VolpianoConverter()
        text, music = converter.convert('(c2) A(f)B(g) C(h)')
        self.assertEqual(music, f'1{MUSIC_WORD_BOUNDARY}c{MUSIC_SYLLABLE_BOUNDARY}d{MUSIC_WORD_BOUNDARY}e')
        self.assertEqual(text, f'{TEXT_WORD_BOUNDARY}A{TEXT_SYLLABLE_BOUNDARY}B{TEXT_WORD_BOUNDARY}C')
        
class TestConversionExamples(unittest.TestCase):

    def test_convert_salve_regina(self):
        #TODO implement
        pass

if __name__ == '__main__':
    unittest.main()