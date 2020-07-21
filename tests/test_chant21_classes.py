import unittest
from music21 import converter
from music21 import metadata
from arpeggio import visit_parse_tree as visitParseTree
from chant21 import chant
from chant21.gabc import ParserGABC
from chant21.gabc import VisitorGABC

class TestChant(unittest.TestCase):
    def test_flatter(self):
        gabc = "(c4) A(fgf/h,gh) (::) B(g) (::)"
        ch = converter.parse(gabc, format='gabc', forceSource=True, storePickle=False)
        m1, m2, m3 = ch.flatter
        clef, n1, n2, n3, n4, bar = m1
        n5, n6, bar2 = m2
        n7, bar3 = m3
        for n in [n1, n2, n3, n4, n5, n6, n7]:
            self.assertIsInstance(n, chant.Note)

    def test_makeMetadata(self):
        gabc = "transcriber:foo;\nname:bar;%%\n(c4) A(fgf/h,gh) (:) B(g) (::)"
        ch = converter.parse(gabc, format='gabc', forceSource=True, storePickle=False)
        self.assertIsInstance(ch[0], chant.Section)
        ch.makeMetadata()
        self.assertIsInstance(ch[0], metadata.Metadata)

    def test_mergeText(self):
        gabc = "(c4) A(fg) (;) (f) (::)"
        parser = ParserGABC(root='body')
        parse = parser.parse(gabc)
        ch = visitParseTree(parse, VisitorGABC())
        ch.joinTextAcrossPausas()
        word1, word2, word3 = ch.elements[0]
        self.assertEqual(len(word1), 1)
        self.assertEqual(len(word2), 1)
        self.assertEqual(len(word3), 1)

        neume1, pausa, neume2 = word2[0]
        self.assertIsInstance(neume1, chant.Neume)
        self.assertIsInstance(pausa, chant.PausaMinor)
        self.assertIsInstance(neume2, chant.Neume)

    def test_mergeWords2(self):
        gabc = "(c4) Ia(d) *(;) (f) (,) (c) (b)"
        parser = ParserGABC()
        parse = parser.parse(gabc)
        ch = visitParseTree(parse, VisitorGABC())
        ch.joinTextAcrossPausas()
        self.assertEqual(len(ch[0].elements), 2)

    def test_mergeWords3(self):
        gabc = "(c4) A(f) (,) (c) B(g)"
        parser = ParserGABC()
        parse = parser.parse(gabc)
        ch = visitParseTree(parse, VisitorGABC())
        ch.joinTextAcrossPausas()
        self.assertEqual(len(ch[0].elements), 3)

class TestToObject(unittest.TestCase):

    def test_body(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(c2) A(f)B(g) (::) C(h) (::)')
        body = visitParseTree(parse, VisitorGABC())
        obj = body.toObject()

        sect1, sect2 = obj['elements']
        self.assertEqual(len(sect1['elements']), 2)
        del sect1['elements']
        self.assertDictEqual(sect1, {'type':'section'})
        self.assertEqual(len(sect2['elements']), 3)
        del sect2['elements']
        self.assertDictEqual(sect2, {'type':'section'})

        del obj['metadata']
        del obj['elements']
        self.assertDictEqual(obj, {'type': 'chant'})
        
    def test_word(self):
        parser = ParserGABC(root='word')
        parse = parser.parse('A(f)B(g)')
        word = visitParseTree(parse, VisitorGABC())
        obj = word.toObject()
        self.assertEqual(len(obj['elements']), 2)
        del obj['elements']
        targetObj = {'type': 'word', 'musicAndTextAligned': None}
        self.assertDictEqual(obj, targetObj)
    
    def test_syllable(self):
        parser = ParserGABC(root='syllable')
        parse = parser.parse('A(f)')
        syll = visitParseTree(parse, VisitorGABC())
        obj = syll.toObject()
        self.assertEqual(len(obj['elements']), 1)
        del obj['elements']
        targetObj = {'type': 'syllable', 'lyric': 'A'}
        self.assertDictEqual(obj, targetObj)

    def test_syllableWithAnnotation(self):
        parser = ParserGABC(root='syllable')
        parse = parser.parse('*(:)')
        syll = visitParseTree(parse, VisitorGABC())
        obj = syll.toObject()
        self.assertEqual(len(obj['elements']), 1)
        del obj['elements']
        targetObj = {'annotation': '*', 'type': 'syllable'}
        self.assertDictEqual(obj, targetObj)

    def test_neume(self):
        n = chant.Neume()
        c = chant.Note('C4')
        d = chant.Note('D4')
        n.append([c, d])
        targetObj = {
            'type': 'neume',
            'elements': [
                {'pitch': 'C4', 'type': 'note'}, 
                {'pitch': 'D4', 'type': 'note'}
            ]
        }
        self.assertDictEqual(n.toObject(), targetObj)

    def test_note(self):
        n = chant.Note('D-4')
        targetObj = {'pitch': 'D-4', 'type': 'note'}
        self.assertDictEqual(n.toObject(), targetObj)

    def test_noteWithEditorialInfo(self):
        n = chant.Note('D-4')
        n.editorial.foo = 'bar'
        targetObj = {'pitch': 'D-4', 'type': 'note', 'editorial': {'foo': 'bar'}}
        self.assertDictEqual(n.toObject(), targetObj)

class TestFromObject(unittest.TestCase):
    
    def test_typeError(self):
        syll = chant.Syllable()
        obj = {'type': 'foo'}
        test_fn = lambda: syll.fromObject(obj)
        self.assertRaises(TypeError, test_fn)

    def test_chant(self):
        ch = chant.Chant()
        obj = {
            'type': 'chant',
            'metadata': {
                'title': 'Hello'
            },
            'elements': []
        }
        ch.fromObject(obj)
        self.assertEqual(len(ch.elements), 0)
        self.assertEqual(ch.editorial.metadata['title'], 'Hello')

    def test_syllable(self):
        syll = chant.Syllable()
        obj = {
            'type': 'syllable',
            'lyric': 'bla',
            'annotation': '*'
        }
        syll.fromObject(obj)
        self.assertEqual(syll.lyric, 'bla')
        self.assertEqual(syll.annotation, '*')
        self.assertEqual(len(syll.elements), 1)
        self.assertIsInstance(syll.elements[0], chant.Annotation)
    
    def test_neume(self):
        n = chant.Neume()
        obj = {
            'type': 'neume',
            'elements': [
                {'pitch': 'C4', 'type': 'note'}, 
                {'pitch': 'D4', 'type': 'note'}
            ]
        }
        n.fromObject(obj)
        self.assertEqual(len(n.elements), 2)
        self.assertIsInstance(n.elements[0], chant.Note)
        self.assertIsInstance(n.elements[1], chant.Note)

    def test_note(self):
        n = chant.Note()
        obj = {
            'type': 'note',
            'pitch': 'D-4', 
            'editorial': {'foo': 'bar'}, 
            'notehead': 'x'
        }
        n.fromObject(obj)
        self.assertEqual(n.pitch.nameWithOctave, 'D-4')
        self.assertEqual(n.notehead, 'x')
        self.assertEqual(n.editorial.foo, 'bar')

class TestToVolpiano(unittest.TestCase):

    def test_pitchConversion(self):
        lowest = chant.Note('F3')
        highest = chant.Note('D6')
        volpianoNotes = '89abcdefghjklmnopqrs'
        i = 0
        for octave in [3,4,5,6]:
            for noteName in 'CDEFGAB':
                n = chant.Note(f'{noteName}{octave}')
                if lowest <= n and n <= highest:
                    volpiano = chant.pitchToVolpiano(n.pitch)
                    self.assertEqual(volpiano, volpianoNotes[i])
                    self.assertEqual(n.volpiano, volpianoNotes[i])
                    i += 1
    
    def test_exceptions(self):
        too_low = chant.Note('E3')
        self.assertRaises(Exception, lambda: chant.pitchToVolpiano(too_low.pitch))

        too_high = chant.Note('E6')
        self.assertRaises(Exception, lambda: chant.pitchToVolpiano(too_high.pitch))

    def test_liquescence(self):
        n = chant.Note('C4')
        n.editorial.liquescence = True
        self.assertEqual(n.volpiano, 'C')
       
if __name__  ==  '__main__':
    unittest.main()