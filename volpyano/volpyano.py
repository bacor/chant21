import music21

VOLPIANO = {
    'bars': '34567',
    'clefs': '12',
    'liquescents': '()ABCDEFGHJKLMNOPQRS',
    'notes': '89abcdefghjklmnopqrs',
    'e_flats': 'wx',
    'b_flats': 'iyz',
    'flats': 'iwxyz',
    'naturals': 'IWXYZ',
    'spaces': '.,-',
    'others': "[]{¶",
}

class Note(music21.note.Note):

    def __init__(self, volpiano, clef, *args, bIsFlat=False, eIsFlat=False, 
        **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.volpiano = volpiano

        # >> Adapted from
        # https://github.com/cuthbertLab/music21/blob/master/music21/volpiano.py#L255
        self.stemDirection = 'noStem'

        if token in VOLPIANO.notes:
            distanceFromLowestLine = VOLPIANO.notes.index(token) - 5
            self.editorial.liquescence = False
        else:
            distanceFromLowestLine = VOLPIANO.liquescents.index(token) - 5
            self.notehead = 'x'
            self.editorial.liquescence = True
        
        clefLowestLine = clef.lowestLine
        diatonicNoteNum = clefLowestLine + distanceFromLowestLine

        self.pitch.diatonicNoteNum = diatonicNoteNum
        if self.pitch.step == 'B' and bIsFlat:
            self.pitch.accidental = pitch.Accidental('flat')
        elif self.pitch.step == 'E' and eIsFlat:
            self.pitch.accidental = pitch.Accidental('flat')
        # <<
        
    @property
    def plain(self):
        """A plain Python object representing the note"""
        return {
            'type': 'note',
            'pitch': None,
            'volpiano': self.volpiano,
        }

class Neume(music21.spanner.Spanner):
    
    def __init__(self, children, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = children

    @property
    def volpiano(self):
        """The Volpiano string representing this neume"""
        return '-'.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the neume"""
        return {
            'type': 'neume',
            'volpiano': self.volpiano,
            'children': [c.plain for c in self.children],
        }

class Syllable(music21.spanner.Spanner):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def text(self):
        return None

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the syllable"""
        return '--'.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the syllable"""
        return {
            'type': 'syllable',
            'text': self.text,
            'children': [c.plain for c in self.children]
        }

class Word(music21.spanner.Spanner):
    
    def __init__(self, children, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = children

    @property
    def text(self):
        raise NotImplementedError

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the word"""
        return '---'.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the word"""
        return {
            'type': 'word',
            'children': 
        }

class Section(music21.spanner.Spanner):
    pass

if __name__ == '__main__':
    S = Syllable('boe')