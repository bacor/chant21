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

def subdict(dictionary, keys):
    return { k: dictionary[k] for k in keys if k in dictionary }
    
class VolpianoNote(music21.note.Note):

    def __init__(self, volpiano='c', clef='g', *args, bIsFlat=False, eIsFlat=False, 
        **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.stemDirection = 'noStem'
        self.bIsFlat = bIsFlat
        self.eIsFlat = eIsFlat
        self.clef = clef
        self.volpiano = volpiano

    @property
    def volpiano(self):
        return self._volpiano

    @volpiano.setter
    def volpiano(self, char):
        self._volpiano = char
        
        # >> Adapted from
        # https://github.com/cuthbertLab/music21/blob/master/music21/volpiano.py#L255
        if char in VOLPIANO['notes']:
            distanceFromLowestLine = VOLPIANO['notes'].index(char) - 6
            self.editorial.liquescence = False
        else:
            distanceFromLowestLine = VOLPIANO['liquescents'].index(char) - 6
            self.notehead = 'x'
            self.editorial.liquescence = True
        
        if self.clef == 'g':
            clef = music21.clef.TrebleClef()
        if self.clef == 'f':
            clef = music21.clef.BassClef()

        clefLowestLine = clef.lowestLine
        diatonicNoteNum = clefLowestLine + distanceFromLowestLine

        self.pitch.diatonicNoteNum = diatonicNoteNum
        if self.pitch.step == 'B' and self.bIsFlat:
            self.pitch.accidental = music21.pitch.Accidental('flat')
        elif self.pitch.step == 'E' and self.eIsFlat:
            self.pitch.accidental = music21.pitch.Accidental('flat')
        # <<

    @property
    def text(self):
        if len(self.lyrics) > 0:
            return self.lyrics[0].rawText

    @text.setter
    def text(self, text):
        self.lyric = text

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

class Neume(music21.stream.Stream):
    
    def __init__(self, volpiano=None, **kwargs):
        """A neume object.

        You can either pass an iterable of `Note` objects, or a volpiano string
        of notes:
        
        ```python
        >>> neume1 = Neume(VolpianoNote('f'), VolpianoNote('g'), VolpianoNote('f'))
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
        super().__init__(**kwargs)

        if volpiano is not None:
            note_kws = subdict(kwargs, ['eIsFlat', 'bIsFlat', 'clef'])
            notes = [VolpianoNote(note, **note_kws) for note in volpiano]
            self.append(notes)

    # def __repr__(self):
    #     """A string representation of the neume"""
    #     return f'<volpyano.Neume {self.volpiano}>'

    def __eq__(self, other):
        """Test neume equality checking equality of the notes"""
        if type(self) != type(other):
            return False
        elif len(self) != len(other):
            return False
        else:
            for i in range(len(self)):
                if self[i] != other[i]:
                    return False
        return True

    @property
    def text(self):
        if len(self.notes) > 0:
            firstNote = self.notes[0]
            return firstNote.lyric
    
    @text.setter
    def text(self, value):
        if len(self.notes) > 0:
            firstNote = self.notes[0]
            firstNote.lyric = value
        else:
            raise Exception('Cannot set text on neume without notes')

    @property
    def volpiano(self):
        """The Volpiano string representing this neume"""
        return ''.join(note.volpiano for note in self.elements)

    @property
    def notes(self):
        return self.getElementsByClass(music21.note.Note)

    @property
    def plain(self):
        """A plain Python object representing the neume"""
        return {
            'type': 'neume',
            'volpiano': self.volpiano,
            'notes': [note.plain for note in self.elements],
        }

class Syllable(music21.stream.Stream):

    def __init__(self, volpiano=None, text=None, **kwargs):
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
        super().__init__(**kwargs)
        
        if volpiano is not None:
            neume_kws = subdict(kwargs, ['eIsFlat', 'bIsFlat', 'clef'])
            neumes = [Neume(n, **neume_kws) for n in volpiano.split('-')]
            self.append(neumes)  
            
        if text is not None:
            self.text = text
        
    # def __repr__(self):
    #     """A string representation of the syllable"""
    #     return f'<volpyano.Syllable {self.text}<{self.volpiano}>>'

    def __eq__(self, other):
        """Test syllable equality by checking text and neumes identity"""
        if type(self) != type(other):
            return False
        elif len(self) != len(other):
            return False
        elif len(self.elements) != len(other.elements):
            return False
        elif self.text != other.text:
            return False
        else:
            for i in range(len(self)):
                if self[i] != other[i]:
                    return False
        return True

    @property
    def text(self):
        if len(self.neumes) > 0:
            firstNeume = self.neumes[0]
            return firstNeume.text

    @text.setter
    def text(self, value):
        if len(self.neumes) > 0:
            firstNeume = self.neumes[0]
            firstNeume.text = value
        else:
            raise Exception('Cannot set text on syllable without neumes')

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the syllable"""
        return '-'.join(neume.volpiano for neume in self.neumes)

    @property
    def neumes(self):
        return self.getElementsByClass(Neume)

    @property
    def plain(self):
        """A plain Python object representing the syllable"""
        return {
            'type': 'syllable',
            'text': self.text,
            'volpiano': self.volpiano,
            'neumes': [neume.plain for neume in self.neumes]
        }

class Word(music21.stream.Stream):
    
    def __init__(self, volpiano=None, text=None, **kwargs):
        super().__init__(**kwargs)

        if volpiano is not None:
            syll_kws = subdict(kwargs, ['eIsFlat', 'bIsFlat', 'clef'])
            syllables = [Syllable(s, **syll_kws) for s in volpiano.split('--')]
            self.append(syllables)
        
        if text is not None:
            self.text = text
        
    # def __repr__(self):
    #     """A string representation of the word"""
    #     syllables = []
    #     for syll in self.syllables:
    #         if len(syll.volpiano) > 5:
    #             syll_str = f'{syll.text}-<{syll.volpiano[:5]}...>'
    #         else:
    #             syll_str = f'{syll.text}-<{syll.volpiano}>'
    #         syllables.append(syll_str)
            
    #     string = ' '.join(syllables)
    #     return f'<volpyano.Word <{string}>'

    def __eq__(self, other):
        """Test equality by checking equality of syllables"""
        if type(self) != type(other):
            return False
        elif len(self) != len(other): 
            return False
        else:
            for i in range(len(self)):
                if self[i] != other[i]:
                    return False
        return True

    @property
    def text(self):
        return '-'.join(syll.text for syll in self.syllables)

    @text.setter
    def text(self, value):
        syllables = value.split('-')
        if len(syllables) != len(self.syllables):
            raise ValueError('The passed number of syllables does not match')
        
        if len(syllables) == 1:
            self.syllables[0].text = syllables[0]
        
        else:
            for i in range(len(self.syllables)):
                if i == 0:
                    self.syllables[i].text = syllables[i] + '-'
                elif i == len(self) - 1:
                    self.syllables[i].text = '-' + syllables[i]
                else:
                    self.syllables[i].text = '-' + syllables[i] + '-'

    @property
    def raw_text(self):
        return ''.join(c.text for c in self.syllables)
    
    @property
    def syllables(self):
        return self.getElementsByClass(Syllable)

    @property
    def volpiano(self):
        """The Volpiano for the music corresponding to the word"""
        return '--'.join(c.volpiano for c in self.syllables)

    @property
    def plain(self):
        """A plain Python object representing the word"""
        return {
            'type': 'word',
            'syllables': [syll.plain for syll in self.syllables]
        }

#TODO implement
class GClef(music21.clef.TrebleClef):
    
    def __init__(self, volpiano='1', text='', **kwargs):
        self.text = text
        self.volpiano = volpiano
        super().__init__(**kwargs)
    
    @property
    def plain(self):
        return {
            'type': 'gClef',
            'volpiano': self.volpiano,
            'text': self.text,
        } 

#TODO implement
class FClef(music21.clef.BassClef):
    
    def __init__(self, volpiano='2', text='', **kwargs):
        self.text = text
        self.volpiano = volpiano
        super().__init__(**kwargs)
    
    @property
    def plain(self):
        return {
            'type': 'fClef',
            'volpiano': self.volpiano,
            'text': self.text,
        } 


class Alteration(music21.base.Music21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure that alterations always occur before their notes
        self.priority = -1

class BreathMark(music21.base.Music21Object):
    """Indicates a breathmark"""
    pass

class NonWord(music21.stream.Stream):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = None
        self.priority = -2

    @property
    def text(self):
        return self.editorial.text

    @text.setter
    def text(self, text):
        self.editorial.text = text

    @property
    def plain(self):
        # TODO
        return {
            
        }

class Chant(object):

    def __init__(self, elements=[]):
        self.elements = elements

    @property
    def plain(self):
        return {
            'type': 'chant',
            'elements': [el.plain for el in self.elements]
        }