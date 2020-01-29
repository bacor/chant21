import music21
from music21 import articulations
from music21 import note
from music21 import stream
from music21 import articulations
from music21 import spanner
from music21 import expressions
from copy import deepcopy

class Chant(music21.stream.Part):
    
    @property
    def flatter(self):
        """A copy of the chant where words, syllables and neumes have been flattened.
        It is not completely flat, since measures are preserved. This method is
        useful for visualizing chants: `ch.flatter.show()` will also show measures
        and barlines, where as `ch.flat.show()` will not."""
        ch = deepcopy(self)
        for measure in ch.getElementsByClass('Measure'):
            for word in measure.getElementsByClass(Word):
                elements = word.flat
                wordOffset = word.offset
                measure.remove(word)
                for el in elements:
                    offset = wordOffset + el.offset
                    if isinstance(el, spanner.Slur): offset = 0.0
                    measure.insert(offset, el)
        return ch

    @property
    def phrases(self):
        """A stream of phrases: the music between two pausas.
        Every pausa is thus turned into a measure boundary"""
        phrases = stream.Part()
        curPhrase = stream.Measure()
        for el in self.flat:
            if not isinstance(el, Pausa):
                curPhrase.append(el)
            else:
                if isinstance(el, articulations.BreathMark):
                    curPhrase.rightBarline = 'dotted'
                phrases.append(curPhrase)
                curPhrase = stream.Measure()
        return phrases

    def addNeumeSlurs(self):
        """Add slurs to all notes in a single neume"""
        neumes = self.recurse(classFilter=Neume)
        for neume in neumes:
            neume.addSlur()
   
class ChantElement(music21.base.Music21Object):

    @property
    def annotation(self):
        return self.editorial.get('annotation')
    
    @annotation.setter
    def annotation(self, value):
        self.editorial.annotation = value

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'light-light'

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
    def flatLyrics(self):
        try:
            return ''.join(syll.lyric for syll in self.syllables)
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
                prevSyll.append(curSyll.elements)
                self.remove(curSyll)
                numSylls -= 1

                # Only merge with next syllable if it has no sung text
                if nextSyll.lyric is None:
                    # TODO we do lose non-sung text here
                    prevSyll.append(nextSyll.elements)
                    self.remove(nextSyll)
                    numSylls -= 1
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

        # TODO long melisma's on a single-syllable word,
        # are those dealt with properly?

class Syllable(ChantElement, music21.stream.Stream):
    @property
    def lyric(self):
        notes = self.flat.notes
        if len(notes) > 0:
            return notes[0].lyric
        else:
            return self.editorial.get('lyric')
    
    @lyric.setter
    def lyric(self, value):
        notes = self.flat.notes
        if len(notes) > 0:
            if type(value) is str:
                l = note.Lyric(text=value, applyRaw=True)
                notes[0].lyrics = [l]
            elif isinstance(value, note.Lyric):
                notes[0].lyrics = [value]
        else:
            self.editorial.lyric = value

    @property
    def neumes(self):
        return self.getElementsByClass(Neume)

    # @property
    # def flatter(self):
    #     syllable = deepcopy(self)
    #     for neume in syllable.neumes:
    #         elements = neume.elements
    #         syllable.remove(neume)
    #         for element in elements:
    #             offset = neume.offset + element.offset
    #             syllable.insert(offset, element)
    #     return syllable

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
    
    def addSlur(self):
        """Adds a slur to the neumes notes"""
        notes = self.notes.elements
        if len(notes) > 1:
            slur = spanner.Slur(notes)
            slur.priority = -1
            self.insert(0, slur)
    
class Note(note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'

class Annotation(expressions.TextExpression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style.alignHorizontal = 'center'
        self.style.fontStyle = 'italic'
        # TODO this has no effect
        self.placement = 'above' 
