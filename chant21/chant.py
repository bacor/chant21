from copy import deepcopy
import json

from music21 import base
from music21 import articulations
from music21 import bar
from music21 import clef
from music21 import note
from music21 import stream
from music21 import articulations
from music21 import spanner
from music21 import expressions

class Chant(stream.Part):
    
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
        Every pausa is thus turned into a section boundary"""
        phrases = stream.Part()
        curPhrase = Section()
        for el in self.flat:
            if not isinstance(el, Pausa):
                curPhrase.append(el)
            else:
                if isinstance(el, articulations.BreathMark):
                    curPhrase.rightBarline = 'dotted'
                phrases.append(curPhrase)
                curPhrase = Section()
        return phrases

    @property
    def sections(self):
        return self.getElementsByClass(Section)

    @property
    def plain(self):
        obj = {
            'type': 'Chant',
            'header': None,
            'elements': [section.plain for section in self.sections]
        }
        return obj

    def toCHSON(self, fp, **kwargs):
        with open(fp, 'w') as handle:
            json.dump(self.plain, handle, **kwargs)
    
    def addNeumeSlurs(self):
        """Add slurs to all notes in a single neume"""
        neumes = self.recurse(classFilter=Neume)
        for neume in neumes:
            neume.addSlur()

class Section(stream.Measure):
    @property
    def plain(self):
        return {
            'type': 'Section',
            'editorial': dict(self.editorial),
            'elements': [el.plain for el in self.elements]
        }

class ChantElement(base.Music21Object):

    @property
    def annotation(self):
        return self.editorial.get('annotation')
    
    @annotation.setter
    def annotation(self, value):
        self.editorial.annotation = value

    @property
    def plain(self):
        obj = {
            'type': type(self).__name__,
        }
        if self.annotation:
            obj['annotation'] = self.annotation
        if self.editorial:
            obj['editorial'] = dict(self.editorial)
        return obj

class Pausa(ChantElement):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -1

class PausaMinima(Pausa, articulations.BreathMark):
    pass

class PausaMinor(Pausa, articulations.BreathMark):
    pass

class PausaMajor(Pausa, bar.Barline):
    pass

class PausaFinalis(Pausa, bar.Barline):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'light-light'

class Clef(ChantElement, clef.TrebleClef):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -2

class Alteration(ChantElement, base.Music21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure that alterations always occur before their notes
        self.priority = -1

class Word(ChantElement, stream.Stream):
    
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
        obj = super().plain
        obj['elements'] = [el.plain for el in self.elements]
        return obj
    
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

class Syllable(ChantElement, stream.Stream):
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

    @property
    def plain(self):
        obj = super().plain
        obj['elements'] = [el.plain for el in self.elements]
        obj['lyric'] = self.lyric
        return obj

class Neume(ChantElement, stream.Stream):
    
    def addSlur(self):
        """Adds a slur to the neumes notes"""
        notes = self.notes.elements
        if len(notes) > 1:
            slur = spanner.Slur(notes)
            slur.priority = -1
            self.insert(0, slur)

    @property
    def plain(self):
        obj = super().plain
        obj['elements'] = [el.plain for el in self.elements]
        return obj
    
class Note(ChantElement, note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'

    @property
    def plain(self):
        obj = super().plain
        obj['pitch'] = self.pitch.nameWithOctave,
        if self.notehead != 'normal':
            obj['notehead'] = self.notehead
        return obj

class Annotation(expressions.TextExpression):
    plain = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style.alignHorizontal = 'center'
        self.style.fontStyle = 'italic'
        # TODO this has no effect
        self.placement = 'above' 