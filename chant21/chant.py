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
from music21 import metadata

#TODO add __repr__ method to classes

class CHSONObject(base.Music21Object):
    """Base class for objects than can be exported to CHSON"""

    def toObject(self, exportChildren=True):
        """Export the object to a plain Python dictionary"""
        obj = dict()
        obj['type'] = type(self).__name__

        if self.hasEditorialInformation:
            obj['editorial'] = dict(self.editorial)
            # Remove annotation from editorial info, since that's already 
            # stored as the objects `annotation` property
            if 'annotation' in obj['editorial']:
                del obj['editorial']['annotation']
                if len(obj['editorial']) == 0:
                    del obj['editorial']

        if hasattr(self, 'annotation') and self.hasAnnotation:
            obj['annotation'] = self.annotation

        if hasattr(self, 'elements') and exportChildren:
            children = [el for el in self.elements if isinstance(el, CHSONObject)]
            obj['elements'] = [child.toObject() for child in children]

        return obj

    def fromObject(self, obj, parent=None, parseChildren=True):
        ownClassName = type(self).__name__
        if not obj['type'] == ownClassName:
            raise TypeError(f'Cannot import object of type `{obj["type"]}` into a {ownClassName}')
        if 'editorial' in obj:
            for key, value in obj['editorial'].items():
                self.editorial[key] = value
        if 'annotation' in obj:
            self.annotation = obj['annotation']
        if 'elements' in obj and parseChildren:
            for childObj in obj['elements']:
                child = CLASSES[childObj['type']]()
                child.fromObject(childObj, parent=self, parseChildren=parseChildren)
                self.append(child)
    
class ChantElement(CHSONObject, base.Music21Object):

    @property
    def annotation(self):
        return self.editorial.get('annotation')
    
    @annotation.setter
    def annotation(self, value):
        self.editorial.annotation = value

    @property
    def hasAnnotation(self):
        """True if the element has a non-empty annotation"""
        return self.annotation is not None

###

class Chant(CHSONObject, stream.Part):
    
    @property
    def flatter(self):
        """A copy of the chant where words, syllables and neumes have been flattened.
        It is not completely flat, since measures are preserved. This method is
        useful for visualizing chants: `ch.flatter.show()` will also show measures
        and barlines, where as `ch.flat.show()` will not."""
        chant = deepcopy(self)
        for measure in chant.getElementsByClass('Measure'):
            for word in measure.getElementsByClass(Word):
                elements = word.flat
                wordOffset = word.offset
                measure.remove(word)
                for el in elements:
                    offset = wordOffset + el.offset
                    if isinstance(el, spanner.Slur): offset = 0.0
                    measure.insert(offset, el)
        
        # Move barlines and breathmarks to their appropriate positions
        chant.makeBarlines()
        chant.makeBreathMarks()
        return chant

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

    def toObject(self):
        metadata = self.editorial.get('metadata', {})
        obj = {
            'type': 'Chant',
            'metadata': metadata,
            'elements': [section.toObject() for section in self.sections]
        }
        return obj

    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        metadata = obj.get('metadata', {})
        self.editorial.metadata = metadata
    
    def toCHSON(self, fp=None, **kwargs):
        if fp is None:
            return json.dumps(self.toObject(), **kwargs)
        else:
            with open(fp, 'w') as handle:
                json.dump(self.toObject(), handle, **kwargs)
    
    def addNeumeSlurs(self):
        """Add slurs to all notes in a single neume"""
        neumes = self.recurse(classFilter=Neume)
        for neume in neumes:
            neume.addSlur()

    def makeBreathMarks(self):
        breathmarks = self.recurse(classFilter=articulations.BreathMark)
        for breathmark in breathmarks:
            prevNote = breathmark.previous(note.Note)
            prevNote.articulations.append(breathmark)
            self.remove(breathmark, recurse=True)
    
    def makeBarlines(self):
        for measure in self.getElementsByClass(stream.Measure):
            barlines = measure.recurse(classFilter=bar.Barline)
            if len(barlines) > 0:
                measure.remove(barlines[-1], recurse=True)
                measure.rightBarline = barlines[-1]

    def makeMetadata(self):
        pass
        # ch.insert(0, metadata.Metadata())
        # if 'title' in header:
        #     ch.metadata.title = header.get('title')
        # for key, value in header.items():
        #     ch.editorial[key] = value
        

class Section(CHSONObject, stream.Measure):
    pass   

class Word(CHSONObject, stream.Stream):
    
    @property
    def flatLyrics(self):
        try:
            return ''.join(syll.lyric for syll in self.syllables)
        except:
            return None
 
    @property
    def syllables(self):
        return self.getElementsByClass(Syllable)

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

    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        self.updateSyllableLyrics()

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

    def toObject(self):
        obj = super().toObject()
        if self.lyric is not None:
            obj['lyric'] = self.lyric
        return obj
    
    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        if 'lyric' in obj:
            self.lyric = obj['lyric']
        if self.hasAnnotation:
            annotation = Annotation(self.annotation)
            self.insert(0, annotation)

class Neume(CHSONObject, stream.Stream):
    
    def addSlur(self):
        """Adds a slur to the neumes notes"""
        notes = self.notes.elements
        if len(notes) > 1:
            slur = spanner.Slur(notes)
            slur.priority = -1
            self.insert(0, slur)
    
class Note(CHSONObject, note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'

    def toObject(self):
        obj = super().toObject()
        obj['pitch'], = self.pitch.nameWithOctave,
        if self.notehead != 'normal':
            obj['notehead'] = self.notehead
        return obj

    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        self.pitch.nameWithOctave = obj['pitch']
        if 'notehead' in obj:
            self.notehead = obj['notehead']

###

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

class Alteration(CHSONObject, base.Music21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure that alterations always occur before their notes
        self.priority = -1

class Annotation(expressions.TextExpression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style.alignHorizontal = 'center'
        self.style.fontStyle = 'italic'
        # TODO this has no effect
        self.placement = 'above' 

##

CLASSES = {
    'Chant': Chant,
    'Section': Section,
    'Word': Word,
    'Syllable': Syllable,
    'Neume': Neume,
    'Note': Note,
    'Clef': Clef,
    'Pausa': Pausa,
    'PausaMinima': PausaMinima,
    'PausaMinor': PausaMinor,
    'PausaMajor': PausaMajor,
    'PausaFinalis': PausaFinalis,
    'Alteration': Alteration,
    'Annotation': Annotation
}