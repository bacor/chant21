import music21
from music21 import articulations
from music21 import note

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

class Clef(ChantElement, music21.clef.TrebleClef):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -2

class Alteration(music21.base.Music21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure that alterations always occur before their notes
        self.priority = -1

class Word(music21.stream.Stream):
    
    @property
    def text(self):
        try:
            return ''.join(syll.text for syll in self.syllables)
        except:
            return None
 
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

    def mergeMelismasWithPausas(self):
        """Merge syllables if they are separated by a syllable containing only a pausa.
        This is often the case on long melismas."""
        if len(self.syllables) == 1: return
        numSylls = len(self.syllables)
        i = 1
        while i < numSylls - 1:
            prevSyll, curSyll, nextSyll = self.syllables[i-1:i+2]
            if len(curSyll.flat) == 1 and isinstance(curSyll[0], articulations.BreathMark):
                prevSyll[0].append(curSyll.elements)
                prevSyll.append(nextSyll.elements)
                # TODO we might loose some text here!
                self.remove(curSyll)
                self.remove(nextSyll)
                numSylls -= 2
            i += 1

    def updateSyllableLyrics(self):
        lyrics = self.flat.lyrics().get(1, False)
        if lyrics is False: return 

        nonEmptyLyrics = [l for l in lyrics if l is not None]
        if len(nonEmptyLyrics) == 1:
            nonEmptyLyrics[0].syllabic = 'single'
        else:
            for syll in nonEmptyLyrics:
                syll.syllabic = 'middle'
            nonEmptyLyrics[0].syllabic = 'begin'
            nonEmptyLyrics[-1].syllabic = 'end'

        # for i, syll in enumerate(syll):
        #     print(syll)
            
        #         print(l)
        
        # if len(self.syllables) == 1:
        #     syll = self.syllables[0]
        #     if len(syll.notes) > 0:
        #         syll.lyrics[0].syllabic = 'single'
        # elif len(word.syllables) > 1:
        #     for syll in word.syllables:
        #         syll.lyrics[0].syllabic = 'middle'
        #     word.syllables[0].lyrics[0].syllabic = 'begin'
        #     word.syllables[-1].lyrics[0].syllabic = 'end'

class Syllable(music21.stream.Stream):

    @property
    def text(self):
        notes = self.flat.notes
        if len(notes) > 0:
            return notes[0].lyric
        else:
            return self.editorial.get('text')
    
    @text.setter
    def text(self, value):
        notes = self.flat.notes
        if len(notes) > 0:
            if type(value) is str:
                lyrics = note.Lyric(text=value, applyRaw=True)
                notes[0].lyrics = [lyrics]
            elif isinstance(value, note.Lyric):
                notes[0].lyrics = [value]
        else:
            self.editorial.text = value

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
    
class Note(note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'