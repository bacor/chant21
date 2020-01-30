import unittest
from music21 import converter
from music21 import metadata

from chant21 import Chant
from chant21 import Section
from chant21 import Note
from chant21 import Neume
from chant21 import Syllable
from chant21 import Word
from chant21 import Alteration
from chant21 import Pausa
from chant21 import Clef
from chant21 import PausaMinima
from chant21 import PausaMinor
from chant21 import PausaMajor
from chant21 import PausaFinalis
from chant21 import Annotation

from chant21 import ParserGABC
from chant21.converterGABC import VisitorGABC
from arpeggio import visit_parse_tree as visitParseTree

class TestChant(unittest.TestCase):
    def test_flatter(self):
        gabc = "(c4) A(fgf/h,gh) (:) B(g) (::)"
        ch = converter.parse(gabc, format='gabc', forceSource=True, storePickle=False)
        measure1, measure2 = ch.flatter
        clef, n1, n2, n3, n4, n5, n6, bar1 = measure1
        n7, bar2 = measure2
        for n in [n1, n2, n3, n4, n5, n6, n7]:
            self.assertIsInstance(n, Note)

    def test_makeMetadata(self):
        gabc = "transcriber:foo;\nname:bar;%%\n(c4) A(fgf/h,gh) (:) B(g) (::)"
        ch = converter.parse(gabc, format='gabc', forceSource=True, storePickle=False)
        self.assertIsInstance(ch[0], Section)
        ch.makeMetadata()
        self.assertIsInstance(ch[0], metadata.Metadata)

class TestToObject(unittest.TestCase):

    def test_body(self):
        parser = ParserGABC(root='body')
        parse = parser.parse('(c2) A(f)B(g) (:) C(h) (::)')
        body = visitParseTree(parse, VisitorGABC())
        obj = body.toObject()

        sect1, sect2 = obj['elements']
        self.assertEqual(len(sect1['elements']), 3)
        del sect1['elements']
        self.assertDictEqual(sect1, {'type':'section'})
        self.assertEqual(len(sect2['elements']), 2)
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
        targetObj = {'type': 'word'}
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
        n = Neume()
        c = Note('C4')
        d = Note('D4')
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
        n = Note('D-4')
        targetObj = {'pitch': 'D-4', 'type': 'note'}
        self.assertDictEqual(n.toObject(), targetObj)

    def test_noteWithEditorialInfo(self):
        n = Note('D-4')
        n.editorial.foo = 'bar'
        targetObj = {'pitch': 'D-4', 'type': 'note', 'editorial': {'foo': 'bar'}}
        self.assertDictEqual(n.toObject(), targetObj)

class TestFromObject(unittest.TestCase):
    
    def test_typeError(self):
        syll = Syllable()
        obj = {'type': 'foo'}
        test_fn = lambda: syll.fromObject(obj)
        self.assertRaises(TypeError, test_fn)

    def test_chant(self):
        chant = Chant()
        obj = {
            'type': 'chant',
            'metadata': {
                'title': 'Hello'
            },
            'elements': []
        }
        chant.fromObject(obj)
        self.assertEqual(len(chant.elements), 0)
        self.assertEqual(chant.editorial.metadata['title'], 'Hello')

    def test_syllable(self):
        syll = Syllable()
        obj = {
            'type': 'syllable',
            'lyric': 'bla',
            'annotation': '*'
        }
        syll.fromObject(obj)
        self.assertEqual(syll.lyric, 'bla')
        self.assertEqual(syll.annotation, '*')
        self.assertEqual(len(syll.elements), 1)
        self.assertIsInstance(syll.elements[0], Annotation)
    
    def test_neume(self):
        n = Neume()
        obj = {
            'type': 'neume',
            'elements': [
                {'pitch': 'C4', 'type': 'note'}, 
                {'pitch': 'D4', 'type': 'note'}
            ]
        }
        n.fromObject(obj)
        self.assertEqual(len(n.elements), 2)
        self.assertIsInstance(n.elements[0], Note)
        self.assertIsInstance(n.elements[1], Note)

    def test_note(self):
        n = Note()
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


if __name__  ==  '__main__':
    unittest.main()