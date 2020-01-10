import unittest
from volpyano import VOLPIANO, Note, Neume, Syllable, Word

class TestNote(unittest.TestCase):
    def test_note_shapes(self):
        note = Note('g')
        self.assertEqual(note.stemDirection, 'noStem')
        self.assertEqual(note.notehead, 'normal')
        
        liquescent = Note('G')
        self.assertEqual(liquescent.stemDirection, 'noStem')
        self.assertEqual(liquescent.notehead, 'x')

    def test_note_steps(self):
        self.assertEqual(Note('8').step, 'F')
        self.assertEqual(Note('9').step, 'G')
        self.assertEqual(Note('a').step, 'A')
        self.assertEqual(Note('b').step, 'B')
        self.assertEqual(Note('c').step, 'C')
        self.assertEqual(Note('d').step, 'D')
        self.assertEqual(Note('e').step, 'E')
        self.assertEqual(Note('f').step, 'F')
        self.assertEqual(Note('g').step, 'G')
        self.assertEqual(Note('h').step, 'A')
        self.assertEqual(Note('j').step, 'B')
        self.assertEqual(Note('k').step, 'C')
        self.assertEqual(Note('l').step, 'D')
        self.assertEqual(Note('m').step, 'E')
        self.assertEqual(Note('n').step, 'F')
        self.assertEqual(Note('o').step, 'G')
        self.assertEqual(Note('p').step, 'A')
        self.assertEqual(Note('q').step, 'B')
        self.assertEqual(Note('r').step, 'C')
        self.assertEqual(Note('s').step, 'D')

    def test_liquescent_steps(self):
        self.assertEqual(Note('(').step, 'F')
        self.assertEqual(Note(')').step, 'G')
        self.assertEqual(Note('A').step, 'A')
        self.assertEqual(Note('B').step, 'B')
        self.assertEqual(Note('C').step, 'C')
        self.assertEqual(Note('D').step, 'D')
        self.assertEqual(Note('E').step, 'E')
        self.assertEqual(Note('F').step, 'F')
        self.assertEqual(Note('G').step, 'G')
        self.assertEqual(Note('H').step, 'A')
        self.assertEqual(Note('J').step, 'B')
        self.assertEqual(Note('K').step, 'C')
        self.assertEqual(Note('L').step, 'D')
        self.assertEqual(Note('M').step, 'E')
        self.assertEqual(Note('N').step, 'F')
        self.assertEqual(Note('O').step, 'G')
        self.assertEqual(Note('P').step, 'A')
        self.assertEqual(Note('Q').step, 'B')
        self.assertEqual(Note('R').step, 'C')
        self.assertEqual(Note('S').step, 'D')

    def test_flats(self):
        # Test B-flats
        for volpiano in 'bBjJqQ':
            b_flat = Note(volpiano, bIsFlat=True)
            self.assertEqual(b_flat.name, 'B-')
            self.assertIsNotNone(b_flat.pitch.accidental)

        # Test E-flats
        for volpiano in 'eEmM':
            e_flat = Note(volpiano, eIsFlat=True)
            self.assertEqual(e_flat.name, 'E-')
            self.assertIsNotNone(e_flat.pitch.accidental)
        
        # All other notes should be unaffected by bIsFlat and eIsFlat
        for volpiano in VOLPIANO['notes'] + VOLPIANO['liquescents']:
            if volpiano not in 'jJbBqQ':
                note = Note(volpiano, bIsFlat=True, eIsFlat=False)
                self.assertIsNone(note.pitch.accidental)
            if volpiano not in 'eEmM':
                note = Note(volpiano, bIsFlat=False, eIsFlat=True)
                self.assertIsNone(note.pitch.accidental)

    def test_volpiano(self):
        self.assertEqual(Note('g').volpiano, 'g')

    def test_plain(self):
        target = {
            'type': 'note',
            'volpiano': 'g',
            'pitch': 'G4',
            'bIsFlat': False,
            'eIsFlat': False
        }
        self.assertDictEqual(Note('g').plain, target)

class TestNeume(unittest.TestCase):

    def test_neume(self):
        a = Note('a')
        b = Note('b')
        c = Note('c')
        neume = Neume(a, b, c)
        pass

    def test_string_init(self):
        neume = Neume('abc')
        self.assertEqual(len(neume.children), 3)
        self.assertEqual(neume.volpiano, 'abc')

    def test_volpiano(self):
        neume = Neume('abc')
        self.assertEqual(neume.volpiano, 'abc')

    def test_plain(self):
        neume = Neume('abc')
        keys = set(neume.plain.keys())
        target_keys = set(['type', 'volpiano', 'children'])
        self.assertSetEqual(keys, target_keys)
        self.assertEqual(neume.plain['volpiano'], neume.volpiano)

    def test_length(self):
        for i in range(1, 10):
            neume = Neume('f' * i)
            self.assertEqual(len(neume), i)

    def test_equality(self):
        self.assertEqual(Neume('fg'), Neume('fg'))
        self.assertNotEqual(Neume('fg'), Neume('fgf'))
        self.assertNotEqual(Neume('fgg'), Neume('fgf'))
        
        # Test different clefs
        self.assertEqual(Neume('fg', clef='f'), Neume('fg', clef='f'))
        self.assertNotEqual(Neume('fg', clef='g'), Neume('fg', clef='f'))

        # Test flats
        self.assertEqual(Neume('bcb', bIsFlat=True), Neume('bcb', bIsFlat=True))
        self.assertNotEqual(Neume('bcb', bIsFlat=True), Neume('bcb', bIsFlat=False))

class TestSyllable(unittest.TestCase):

    def test_syllable(self):
        neume1 = Neume(Note('f'), Note('g'), Note('f'))
        neume2 = Neume(Note('e'), Note('f'))
        syll = Syllable('hey', (neume1, neume2))
        self.assertEqual(syll.text, 'hey')
    
    def test_string_init(self):
        syll = Syllable('hey', 'fgf-fg')
        self.assertEqual(syll.text, 'hey')
    
    def test_volpiano(self):
        syll = Syllable('hey', 'fgf-ef')
        self.assertEqual(syll.volpiano, 'fgf-ef')

    def test_plain(self):
        syll = Syllable('hey', 'fgf-ef')
        keys = set(syll.plain.keys())
        target_keys = set(['type', 'text', 'volpiano', 'children'])
        self.assertSetEqual(keys, target_keys) 

    def test_equality(self):
        self.assertEqual(Syllable('foo', 'fgf-ef'), Syllable('foo', 'fgf-ef'))
        self.assertNotEqual(Syllable('foo', 'fgf-ef'), Syllable('bar', 'fgf-ef'))
        self.assertNotEqual(Syllable('foo', 'fg-ef-f'), Syllable('foo', 'fg-ef'))
        self.assertNotEqual(Syllable('foo', 'fg-ff'), Syllable('foo', 'fg-ef'))

class TestWord(unittest.TestCase):
    def test_word(self):
        he = Syllable('He', 'fgf')
        llo = Syllable('llo', 'fg')
        hello = Word(he, llo)

    def test_string_init(self):
        hello = Word('he-llo', 'fgf--fgg-ffg')
        pass

    def test_volpiano(self):
        hello = Word('he-llo', 'fgf--fgg-ffg')
        self.assertEqual(hello.volpiano, 'fgf--fgg-ffg')

    def test_text(self):
        hello = Word('he-llo', 'fgf--fgg-ffg')
        self.assertEqual(hello.text, 'he-llo')
        self.assertEqual(hello.raw_text, 'hello')


if __name__ == '__main__':
    unittest.main()