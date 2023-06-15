"""Unittests for the GABC to Chant21 converter"""
import unittest
from arpeggio import visit_parse_tree as visitParseTree
from music21 import articulations
from music21 import converter
from music21 import note as note21
from music21 import clef as clef21
from chant21 import chant
from chant21.gabc import ParserGABC
from chant21.gabc import VisitorGABC
from chant21.gabc import gabcPositionToStep
from chant21.gabc import MissingClef
from chant21.gabc import AlterationWarning

def parseGABC(string):
    return converter.parse(string, format='gabc', forceSource=True, storePickle=False)

class TestFile(unittest.TestCase):
    def test_file(self):
        parser = ParserGABC(root='file')
        fileStr = 'title:Title!;\nattr1:value1;%%\n\n(c2) a(f)b(g) c(h)\ni(j)'
        parse = parser.parse(fileStr)
        ch = visitParseTree(parse, VisitorGABC())

        metadata = ch.editorial.metadata
        self.assertEqual(metadata['title'], 'Title!')
        self.assertEqual(metadata['attr1'], 'value1')
        
        notes = ch.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'D')
        self.assertEqual(notes[2].name, 'E')
        self.assertEqual(notes[3].name, 'G')

    def test_fileWithoutHeader(self):
        parser = ParserGABC(root='file')
        fileStr = '(c2) a(f)b(g) c(h)\ni(j)'
        parse = parser.parse(fileStr)
        ch = visitParseTree(parse, VisitorGABC())
        notes = ch.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'D')
        self.assertEqual(notes[2].name, 'E')
        self.assertEqual(notes[3].name, 'G')

    def test_header(self):
        parser = ParserGABC(root='header')
        parse = parser.parse('attr1: value1;\nattr2:value2;')
        header = visitParseTree(parse, VisitorGABC())
        target = dict(attr1='value1', attr2='value2')
        self.assertDictEqual(header, target)

    def test_headerEmptyValue(self):
        parser = ParserGABC(root='header')
        parse = parser.parse('attr1:;')
        header = visitParseTree(parse, VisitorGABC())
        self.assertDictEqual(header, {'attr1': ''})

    def test_headerWhitespaceValue(self):
        parser = ParserGABC(root='header')
        parse = parser.parse('attr1: ;\nattr2:    ;')
        header = visitParseTree(parse, VisitorGABC())
        self.assertDictEqual(header, {'attr1': '', 'attr2': ''})

    def test_multipleHeaders(self):
        parser = ParserGABC()
        fileStr = 'attr1:value1;\n%%\nattr2:value2;\n%%\n(c2) A(f)'
        parse = parser.parse(fileStr)
        ch = visitParseTree(parse, VisitorGABC())
        metadata = {'attr1': 'value1', 'attr2': 'value2'}
        self.assertEqual(metadata['attr1'], 'value1')
        self.assertEqual(metadata['attr2'], 'value2')
        
class TestGABCPitchConversion(unittest.TestCase):
    def test_positions(self):
        self.assertEqual(gabcPositionToStep('c', 'c1'), 'B3')
        self.assertEqual(gabcPositionToStep('d', 'c1'), 'C4')
        self.assertEqual(gabcPositionToStep('e', 'c1'), 'D4')
        
        self.assertEqual(gabcPositionToStep('e', 'c2'), 'B4')
        self.assertEqual(gabcPositionToStep('f', 'c2'), 'C5')
        self.assertEqual(gabcPositionToStep('g', 'c2'), 'D5')
        self.assertEqual(gabcPositionToStep('h', 'c2'), 'E5')

        self.assertEqual(gabcPositionToStep('g', 'c3'), 'B4')
        self.assertEqual(gabcPositionToStep('h', 'c3'), 'C5')
        self.assertEqual(gabcPositionToStep('i', 'c3'), 'D5')

class TestAlterations(unittest.TestCase):
    def test_alterations(self):
        parser = ParserGABC(root='alteration')
        for alteration in 'xy':
            parse = parser.parse(f'f{alteration}')
            element = visitParseTree(parse, VisitorGABC())
            ed = element.editorial
            self.assertIsInstance(element, chant.Alteration)
            self.assertEqual(ed.gabcPosition, 'f')
            self.assertEqual(ed.gabcAlteration, alteration)

    def test_flats(self):
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) a(exee,e)')
        stream = visitParseTree(parse, VisitorGABC())
        flat = stream.flat[1]
        self.assertIsInstance(flat, chant.Alteration)
        self.assertEqual(flat.pitch.step, 'B')

        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[0].pitch.accidental.name, 'flat')
        self.assertEqual(notes[1].name, 'B-')
        self.assertEqual(notes[1].pitch.accidental.name, 'flat')
        self.assertEqual(notes[2].name, 'B')
        self.assertIsNone(notes[2].pitch.accidental)
    
    def test_naturals(self): 
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) a(eexeeyee,e)')
        stream = visitParseTree(parse, VisitorGABC())
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
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) (exe,fe)')
        stream = visitParseTree(parse, VisitorGABC())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[1].name, 'C')
        self.assertEqual(notes[2].name, 'B')

    def test_wordBoundaries(self):
        """Test whether word boundaries reset accidentals"""
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) a(exfe) c(e)')
        stream = visitParseTree(parse, VisitorGABC())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'B-')
        self.assertEqual(notes[2].name, 'B')
    
    def test_syllableBoundaries(self):
        """Test whether flats are NOT reset by syllable boundaries"""
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) a(exe)b(e)')
        stream = visitParseTree(parse, VisitorGABC())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')
        self.assertEqual(notes[1].name, 'B-')

    def test_flatClefs(self):
        """Test whether flats are NOT reset by syllable boundaries"""
        parser = ParserGABC(root='body')    
        parse = parser.parse('(cb2) (e)')
        stream = visitParseTree(parse, VisitorGABC())
        notes = stream.flat.notes
        self.assertEqual(notes[0].name, 'B-')

    def test_naturalsInFlatClefs(self):
        """Test whether naturals work in flat clefs"""
        parser = ParserGABC(root='body')    
        parse = parser.parse('(cb2) (eeyee,e) (e)')
        stream = visitParseTree(parse, VisitorGABC())
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

    def test_polyphonicAlterations(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('f{ix}g')
        elements = visitParseTree(parse, VisitorGABC())
        n1, alt, n2 = elements
        self.assertIsInstance(n1, chant.Neume)
        self.assertIsInstance(alt, chant.Flat)
        self.assertIsInstance(n2, chant.Neume)
      
class TestText(unittest.TestCase):

    def test_text(self):
        parser = ParserGABC(root='body')    
        parse = parser.parse('a(c2) word(e)1(f) word2(g)')
        ch = visitParseTree(parse, VisitorGABC())
        w1, w2, w3 = ch[0]
        self.assertEqual(w1.flatLyrics, 'a')
        self.assertEqual(w2.flatLyrics, 'word1')
        self.assertEqual(w3.flatLyrics, 'word2')

        syll1, syll2 = w2.elements
        self.assertEqual(syll1.lyric, 'word')
        self.assertEqual(syll2.lyric, '1')
        self.assertEqual(syll1.flat.notes[0].lyric, 'word')
        self.assertEqual(syll2.flat.notes[0].lyric, '1')

    def test_textAfterAccidental(self):
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) bla(eye)')
        ch = visitParseTree(parse, VisitorGABC())
        word1, word2 = ch[0]
        self.assertIsNone(word1.flatLyrics)
        self.assertEqual(word2.flatLyrics, 'bla')
        note = word2.flat.notes[0]
        self.assertEqual(note.lyric, 'bla')
    
    def test_singleSyllable(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('s1(f)')
        word = visitParseTree(parse, VisitorGABC())
        n = word.flat.notes[0]
        self.assertEqual(n.lyrics[0].syllabic, 'single')

    def test_twoSyllables(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('s1(f)s2(f)')
        word = visitParseTree(parse, VisitorGABC())
        syll1, syll2 = word.syllables
        lyric1 = syll1.flat.notes[0].lyrics[0]
        lyric2 = syll2.flat.notes[0].lyrics[0]
        self.assertEqual(lyric1.syllabic, 'begin')
        self.assertEqual(lyric2.syllabic, 'end')

    def test_threeOrMoreSyllables(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('s1(f)s2(f)s3(g)s4(f)')
        word = visitParseTree(parse, VisitorGABC())
        s1, s2, s3, s4 = word.syllables
        lyric1 = s1.flat.notes[0].lyrics[0]
        lyric2 = s2.flat.notes[0].lyrics[0]
        lyric3 = s3.flat.notes[0].lyrics[0]
        lyric4 = s4.flat.notes[0].lyrics[0]
        self.assertEqual(lyric1.syllabic, 'begin')
        self.assertEqual(lyric2.syllabic, 'middle')
        self.assertEqual(lyric3.syllabic, 'middle')
        self.assertEqual(lyric4.syllabic, 'end')

    def test_annotations(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('<i>i.</i>(f)')
        syll1, = visitParseTree(parse, VisitorGABC())
        self.assertEqual(syll1.annotation, 'i.')
        self.assertIsNone(syll1.lyric)

    def test_annotationsSpaces(self):
        parser = ParserGABC(root='body')    
        parse = parser.parse('(c2) A(f) * (f)')
        ch = visitParseTree(parse, VisitorGABC())
        clef, w1, w2 = ch[0]
        self.assertEqual(w2[0].annotation, '*')


    def test_annotationsAndLyrics(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('A<i>i.</i> B(f)')
        syll1, = visitParseTree(parse, VisitorGABC())
        self.assertEqual(syll1.annotation, 'A<i>i.</i> B')
        self.assertIsNone(syll1.lyric)

    def test_lyric(self):
        parser = ParserGABC(root='word')    
        parse = parser.parse('bla(f)')
        syll1, = visitParseTree(parse, VisitorGABC())
        self.assertIsNone(syll1.annotation)
        self.assertEqual(syll1.lyric, 'bla')
    
    # def test_annotationsInBody(self):
    #     parser = ParserGABC(root='body')    
    #     parse = parser.parse('(c2) a(f)b(g) <i>i.</i>(:) c(f) (::)')
    #     ch = visitParseTree(parse, VisitorGABC())
        

class TestBarClefs(unittest.TestCase):
    def test_pausa(self):
        parser = ParserGABC(root='pausa')
        pausaTypes = [
            (chant.PausaFinalis, ['::']),
            (chant.PausaMajor, [':', ':?', ':\'']),
            (chant.PausaMinor, [';', ';1', ';2']),
            (chant.PausaMinima, [',', ',_', ',0', ',1', '`'])
        ]
        for pausaClass, examples in pausaTypes:
            for gabc in examples:
                parse = parser.parse(gabc)
                element = visitParseTree(parse, VisitorGABC())
                self.assertIsInstance(element, pausaClass)
                self.assertEqual(element.editorial.gabc, gabc)

    def test_clefs(self):
        parser = ParserGABC(root='clef')
        for clef in ['c1', 'c2', 'c3', 'c4', 'f3', 'f4', 'cb3', 'cb4']:
            parse = parser.parse(clef)
            element = visitParseTree(parse, VisitorGABC())
            self.assertIsInstance(element, clef21.TrebleClef)
            self.assertEqual(element.editorial.gabc, clef)

    def test_missingClef(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('a(fgf)')
        test_fn = lambda: visitParseTree(parse, VisitorGABC())
        self.assertRaises(MissingClef, test_fn)

class TestSyllables(unittest.TestCase):
    def test_syllable(self):
        parser = ParserGABC(root='syllable')
        parse = parser.parse('A(fg)')
        syllable = visitParseTree(parse, VisitorGABC())
        self.assertEqual(syllable.lyric, 'A')
        self.assertEqual(len(syllable.flat.notes), 2)
        self.assertEqual(len(syllable), 1)

    def test_multipleNeumes(self):
        parser = ParserGABC(root='syllable')
        parse = parser.parse('A(fg/fg)')
        syllable = visitParseTree(parse, VisitorGABC())
        self.assertEqual(syllable.lyric, 'A')
        self.assertEqual(len(syllable.flat.notes), 4)
        self.assertEqual(len(syllable), 2)
        
    def test_syllablesWithCommas(self):
        parser = ParserGABC(root='word')    
        gabc = 'a(f)(,)(f)b(f)(,)(f)c(g)'
        parse = parser.parse(gabc)
        word = visitParseTree(parse, VisitorGABC())
        word.joinSyllablesAcrossPausas()
        self.assertEqual(len(word), 3)
        syll1, syll2, syll3 = word.elements
        self.assertEqual(len(syll1.flat), 3)
        self.assertIsInstance(syll1.flat[1], chant.Pausa)
        self.assertEqual(len(syll2.flat), 3)
        self.assertIsInstance(syll2.flat[1], chant.Pausa)
        self.assertEqual(len(syll3.flat), 1)

    def test_syllablesWithCommas2(self):
        parser = ParserGABC(root='word')    
        gabc = 'a(fg/gh)(,)(hi/ij)'
        parse = parser.parse(gabc)
        word = visitParseTree(parse, VisitorGABC())
        word.joinSyllablesAcrossPausas()
        self.assertEqual(len(word), 1)
        neume1, neume2, comma, neume3, neume4 = word[0].elements
        self.assertIsInstance(neume1, chant.Neume)
        self.assertIsInstance(neume2, chant.Neume)
        self.assertIsInstance(comma, chant.Pausa)
        self.assertIsInstance(neume3, chant.Neume)
        self.assertIsInstance(neume4, chant.Neume)
                
    def test_syllablesWithCommas3(self):
        """Test whether a new syllable starts if the next syllable
        has sung text"""
        parser = ParserGABC(root='word')    
        gabc = 'a(fg/gh)(,)b(hi/ij)'
        parse = parser.parse(gabc)
        word = visitParseTree(parse, VisitorGABC())
        word.joinSyllablesAcrossPausas()
        (neume1, neume2, comma), (neume3, neume4) = word
        self.assertIsInstance(neume1, chant.Neume)
        self.assertIsInstance(neume2, chant.Neume)
        self.assertIsInstance(comma, chant.Pausa)
        self.assertIsInstance(neume3, chant.Neume)
        self.assertIsInstance(neume4, chant.Neume)

    def test_multipleSyllablesWithCommas(self):
        parser = ParserGABC(root='word')    
        gabc = 'a(f)(,)(f)(,)(f)b(f)'
        parse = parser.parse(gabc)
        word = visitParseTree(parse, VisitorGABC())
        word.joinSyllablesAcrossPausas()
        self.assertEqual(len(word), 2)
        syll1, syll2 = word.elements
        self.assertEqual(len(syll1.flat), 5)
        self.assertIsInstance(syll1.flat[1], chant.Pausa)
        self.assertEqual(len(syll2.flat), 1)
    
    def test_multipleSyllablesWithCommas2(self):
        """Test whether syllables separated by commas are correctly
        merged; including the last one"""
        parser = ParserGABC(root='word')    
        gabc = 'a(f)(,)(f)(,)(f)'
        parse = parser.parse(gabc)
        word = visitParseTree(parse, VisitorGABC())
        word.joinSyllablesAcrossPausas()
        self.assertEqual(len(word), 1)

class TestNeumes(unittest.TestCase):

    def test_singleNeume(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('fgf')
        elements = visitParseTree(parse, VisitorGABC())
        self.assertEqual(len(elements), 1)
        
        neume = elements[0]
        self.assertEqual(len(neume), 3)
        self.assertIsInstance(neume[0], note21.Note)
        self.assertIsInstance(neume[1], note21.Note)
        self.assertIsInstance(neume[2], note21.Note)
        self.assertEqual(neume[0].editorial.gabcPosition, 'f')
        self.assertEqual(neume[1].editorial.gabcPosition, 'g')
        self.assertEqual(neume[2].editorial.gabcPosition, 'f')

    def test_multipleNeumes(self):
        parser = ParserGABC(root='music')
        parse = parser.parse('eh/hi')
        elements = visitParseTree(parse, VisitorGABC())
        self.assertEqual(len(elements), 2)
        self.assertIsInstance(elements[0], chant.Neume)
        self.assertEqual(len(elements[0]), 2)
        self.assertIsInstance(elements[1], chant.Neume)
        self.assertEqual(len(elements[1]), 2)

    def test_articulationBeforeComma(self):
        parser = ParserGABC(root='body')
        parse = parser.parse("(c2) A(a,d)")
        ch = visitParseTree(parse, VisitorGABC())
        ch.makeBreathMarks()
        clef, n1, n2 = ch.flat
        self.assertIsInstance(clef, chant.Clef)
        self.assertIsInstance(n1, chant.Note)
        self.assertIsInstance(n2, chant.Note)
        self.assertEqual(len(n1.articulations), 1)
    
class TestNotes(unittest.TestCase):
    
    def test_noteSuffixes(self):
        parser = ParserGABC(root='note')
        parse = parser.parse('fs<.')
        note = visitParseTree(parse, VisitorGABC())
        ed = note.editorial
        self.assertEqual(ed.gabcPosition, 'f')
        self.assertTrue({'neumeShape': 's<'} in ed.gabcSuffixes)
        self.assertTrue({'rhythmicSign': '.'} in ed.gabcSuffixes)
    
    def test_notePrefix(self):
        parser = ParserGABC(root='note')
        parse = parser.parse('-f')
        note = visitParseTree(parse, VisitorGABC())
        ed = note.editorial
        self.assertEqual(ed.gabcPosition, 'f')
        self.assertEqual(ed.gabcPrefix, '-')
        self.assertTrue(ed.liquescence)

    def test_positions(self):
        parser = ParserGABC(root='position')
        for position in 'abcdefghijklmABCDEFGHIJKLM':
            parse = parser.parse(position)
            output = visitParseTree(parse, VisitorGABC())
            self.assertEqual(output, position)

    def test_emptyNotes(self):
        parser = ParserGABC(root='note')
        parse = parser.parse('gr')
        n = visitParseTree(parse, VisitorGABC())
        self.assertFalse(n.noteheadFill, False)
        self.assertTrue({'emptyNote': 'r'} in n.editorial.gabcSuffixes)

    def test_multipleSuffixes(self):
        parser = ParserGABC(root='note')
        parse = parser.parse('go1')
        n = visitParseTree(parse, VisitorGABC())
        suffixes = n.editorial.gabcSuffixes
        self.assertTrue({'neumeShape': 'o'} in suffixes)
        self.assertTrue({'neumeShape': '1'} in suffixes)
        self.assertEqual(n.editorial.gabcPosition, 'g')

class TestIgnoredFeatures(unittest.TestCase):
    def test_macros(self):
        """Test whether a file with macro's is converted properly despite them"""
        parser = ParserGABC(root='file')
        parse = parser.parse('%%\ndef-m1:\grealign;\ndef-m2:\grealign;\n(c2) a(f)')
        elements = visitParseTree(parse, VisitorGABC())
        self.assertTrue(True)

class TestConverter(unittest.TestCase):

    def test_conversion(self):
        gabc = '(c2) a(f)b(g) c(h)\ni(j)'
        ch = parseGABC(gabc)
        notes = ch.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'D')
        self.assertEqual(notes[2].name, 'E')
        self.assertEqual(notes[3].name, 'G')


    def test_conversionFileContents(self):
        fileStr = 'title:Title!;\nattr1:value1;%%\n\n(c2) a(f)b(g) c(h)\ni(j)'
        ch = parseGABC(fileStr)
        notes = ch.flat.notes
        self.assertEqual(notes[0].name, 'C')
        self.assertEqual(notes[1].name, 'D')
        self.assertEqual(notes[2].name, 'E')
        self.assertEqual(notes[3].name, 'G')

if __name__ == '__main__':
    unittest.main()