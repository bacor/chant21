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

    def __init__(self, volpiano, clef='g', *args, bIsFlat=False, eIsFlat=False, 
        **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.volpiano = volpiano
        self.bIsFlat = bIsFlat
        self.eIsFlat = eIsFlat

        # >> Adapted from
        # https://github.com/cuthbertLab/music21/blob/master/music21/volpiano.py#L255
        self.stemDirection = 'noStem'

        if volpiano in VOLPIANO['notes']:
            distanceFromLowestLine = VOLPIANO['notes'].index(volpiano) - 6
            self.editorial.liquescence = False
        else:
            distanceFromLowestLine = VOLPIANO['liquescents'].index(volpiano) - 6
            self.notehead = 'x'
            self.editorial.liquescence = True
        
        if clef == 'g':
            clef = music21.clef.TrebleClef()
        if clef == 'f':
            clef = music21.clef.BassClef()

        clefLowestLine = clef.lowestLine
        diatonicNoteNum = clefLowestLine + distanceFromLowestLine

        self.pitch.diatonicNoteNum = diatonicNoteNum
        if self.pitch.step == 'B' and bIsFlat:
            self.pitch.accidental = music21.pitch.Accidental('flat')
        elif self.pitch.step == 'E' and eIsFlat:
            self.pitch.accidental = music21.pitch.Accidental('flat')
        # <<
        
    @property
    def plain(self):
        """A plain Python object representing the note"""
        return {
            'type': 'note',
            'volpiano': self.volpiano,
            'pitch': str(self.pitch),
            'bIsFlat': self.bIsFlat,
            'eIsFlat': self.eIsFlat,
        }

class Neume(music21.spanner.Spanner):
    
    def __init__(self, *children, **kwargs):
        """A neume object.

        You can either pass an iterable of `Note` objects, or a volpiano string
        of notes:
        
        ```python
        >>> neume1 = Neume(Note('f'), Note('g'), Note('f'))
        >>> neume2 = Neume('fgf')
        >>> neume1 == neume2
        True
        ```
        
        Args:
            children (iterable or string): either an iterable of `Note`
                objects, or a string of volpiano notes. 
            eIsFlat (boolean, optional): whether the E is flat. Only used
                if children are specified as a volpiano string. Defaults
                to False.
            eIsFlat (boolean, optional): whether the B is flat. Only used
                if children are specified as a volpiano string. Defaults
                to False.
            clef (string, optional): the clef to use (`'g'` or `'f'`). Only 
                used if children are specified as a volpiano string. Defaults
                to `'g'`.
        """
        if type(children[0]) == str:
            note_kws = {
                'eIsFlat': kwargs.get('eIsFlat', False),
                'bIsFlat': kwargs.get('bIsFlat', False),
                'clef': kwargs.get('clef', 'g'),
            }
            self.children = [Note(note, **note_kws) for note in children[0]]
        else:
            self.children = children
        
        super().__init__(*self.children, **kwargs)

    def __repr__(self):
        """A string representation of the neume"""
        return f'<volpyano.neume.Neume {self.volpiano}>'

    def __eq__(self, other):
        """Test neume equality checking equality of the notes"""
        if type(self) != type(other):
            return False
        elif self.length != other.length:
            return False
        else:
            for i in range(self.length):
                if self.children[i] != other.children[i]:
                    return False
        return True
    
    @property
    def length(self):
        """The number of notes"""
        return len(self.children)

    @property
    def volpiano(self):
        """The Volpiano string representing this neume"""
        return ''.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the neume"""
        return {
            'type': 'neume',
            'volpiano': self.volpiano,
            'children': [c.plain for c in self.children],
        }


class Syllable(music21.spanner.Spanner):

    def __init__(self, text, neumes, **kwargs):
        """A Syllable.

        You can either pass an iterable of `Neume` objects, or a volpiano string
        of neumes:
        
        ```python
        >>> syll1 = Syllable('text', Neume('fgf'), Neume('ef'))
        >>> syll2 = Syllable('text', 'fgf-ef')
        >>> syll1 == syll2
        True
        ```
        
        Args:
            text (string): The syllable text (lyrics)
            neumes (string or iterable): This can either be an iterable of 
                `Neume` objects, or a volpiano syllable string.
        """
        self.text = text
        if type(neumes[0]) == str:
            neume_kws = {
                'eIsFlat': kwargs.get('eIsFlat', False),
                'bIsFlat': kwargs.get('bIsFlat', False),
                'clef': kwargs.get('clef', 'g'),
            }
            neumes = neumes.split('-')
            self.children = [Neume(c, **neume_kws) for c in neumes]
        else:
            self.children = neumes
        
        super().__init__(self.children, **kwargs)
        
    def __repr__(self):
        """A string representation of the syllable"""
        return f'<volpyano.syllable.Syllable {self.text}<{self.volpiano}>>'

    def __eq__(self, other):
        """Test syllable equality by checking text and neumes identity"""
        if type(self) != type(other):
            return False
        elif self.length != other.length:
            return False
        elif self.text != other.text:
            return False
        else:
            for i in range(self.length):
                if self.children[i] != other.children[i]:
                    return False
        return True

    @property
    def length(self):
        """The number of neumes"""
        return len(self.children)

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the syllable"""
        return '-'.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the syllable"""
        return {
            'type': 'syllable',
            'text': self.text,
            'volpiano': self.volpiano,
            'children': [c.plain for c in self.children]
        }

class Word(music21.spanner.Spanner):
    
    def __init__(self, *syllables, **kwargs):
        print(syllables)
        if len(syllables) == 2 and type(syllables[0]) == str:
            syll_kws = {
                'eIsFlat': kwargs.get('eIsFlat', False),
                'bIsFlat': kwargs.get('bIsFlat', False),
                'clef': kwargs.get('clef', 'g'),
            }
            text, volpiano = syllables
            txt_syllables = text.split('-')
            vol_syllables = volpiano.split('--')
            self.children = [Syllable(txt, vol, **syll_kws) 
                             for txt, vol in zip(txt_syllables, vol_syllables)]
        else:
            self.children = syllables

        super().__init__(self.children, **kwargs)

    def __repr__(self):
        """A string representation of the word"""
        syllables = []
        for syll in self.children:
            if len(syll.volpiano) > 5:
                syll_str = f'{syll.text}-<{syll.volpiano[:5]}...>'
            else:
                syll_str = f'{syll.text}-<{syll.volpiano}>'
            syllables.append(syll_str)
        string = ' '.join(syllables)
        return f'<volpyano.Word <{string}>'

    def __eq__(self, other):
        """Test equality by checking equality of syllables"""
        if type(self) != type(other):
            return False
        elif self.length != other.length: 
            return False
        else:
            for i in range(self.length):
                if self.children[i] != other.children[i]:
                    return False
        return True

    @property
    def length(self):
        """The number of syllables"""
        return len(self.children)

    @property
    def text(self):
        return '-'.join(c.text for c in self.children)

    @property
    def raw_text(self):
        return ''.join(c.text for c in self.children)

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the word"""
        return '--'.join(c.volpiano for c in self.children)

    @property
    def plain(self):
        """A plain Python object representing the word"""
        return {
            'type': 'word',
            'children': self.children
        }