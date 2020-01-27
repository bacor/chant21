import music21

class Chant(music21.stream.Part):
    pass

class ChantElement(music21.base.Music21Object):
    @property
    def text(self):
        return self.editorial.get('text', None)

    @text.setter
    def text(self, text):
        self.editorial.text = text

    @property
    def plain(self):
        raise NotImplementedError()

class NoMusic(ChantElement):
    """An element containing only text, and no music"""
    pass

class Pausa(ChantElement):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -1

class PausaMinima(Pausa, music21.articulations.BreathMark):
    pass

class PausaMinor(Pausa, music21.articulations.BreathMark):
    pass

class PausaMajor(Pausa, music21.bar.Barline):
    pass

class PausaFinalis(Pausa, music21.bar.Barline):
    pass

# class Pausa(ChantElement, music21.articulations.BreathMark):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.priority = -1

class Barline(ChantElement, music21.bar.Barline):
    pass

class Clef(ChantElement, music21.clef.TrebleClef):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -2

class Alteration(music21.base.Music21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure that alterations always occur before their notes
        self.priority = -1

class Word(ChantElement, music21.stream.Stream):
    
    @property
    def text(self):
        return ''.join(syll.text for syll in self.syllables)
 
    @property
    def syllables(self):
        return self.getElementsByClass(Syllable)

    @property
    def plain(self):
        """A plain Python object representing the word"""
        return {
            'type': 'word',
            'syllables': [syll.plain for syll in self.syllables]
        }

class Syllable(music21.stream.Stream):

    @property
    def text(self):
        if len(self.elements) > 0:
            return self.elements[0].text
        # notes = self.flat.notes
        # if len(notes) > 0:
        #     if notes[0].lyric:
        #         return notes[0].lyric
        #     else:
        #         return self.editorial.get('text', None)

    @text.setter
    def text(self, value):
        if len(self.elements) > 0:
            self.elements[0].text = value
        # notes = self.flat.notes
        # if len(notes) > 0:
        #     if type(value) is str:
        #         notes[0].lyric = value
        #     elif isinstance(value, music21.note.Lyric):
        #         notes[0].lyrics = [value]
        # else:
        #     self.editorial.text = value
        #     # raise Exception('Cannot set text on syllable without notes')
    
    @property
    def lyrics(self):
        notes = self.flat.notes
        if len(notes) > 0:
            return notes[0].lyrics 

    @property
    def neumes(self):
        return self.getElementsByClass(Neume)

    @property
    def plain(self):
        """A plain Python object representing the syllable"""
        return {
            'type': 'syllable',
            'text': self.text,
            'neumes': [neume.plain for neume in self.neumes]
        }

class Neume(music21.stream.Stream):
   
    @property
    def plain(self):
        """A plain Python object representing the neume"""
        return {
            'type': 'neume',
            'notes': [note.plain for note in self.elements],
        }
    
class Note(music21.note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'