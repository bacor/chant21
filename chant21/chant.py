# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         chant.py
# Purpose:      the main chant classes
#
# Authors:      Bas Cornelissen
#
# Copyright:    Copyright © 2020-present Bas Cornelissen
# License:      see LICENSE
# ------------------------------------------------------------------------------
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
from music21 import pitch

from .html import toFile
from .html import toWidget
from . import __version__

def pitchToVolpiano(pitch, liquescence=False):
    """Convert a music21.pitch object to a volpiano character"""
    volpianoLiquescents = '()ABCDEFGHJKLMNOPQRS'
    volpianoNotes = '89abcdefghjklmnopqrs'
    # Adapted from music21.volpiano.volpiano
    # Currently only support TrebleClef; could change this later:
    # clef = self.getContextByClass('Clef')
    # clefLowestLine = clef.lowestLine
    clefLowestLine = 31
    distanceFromLowestLine = pitch.diatonicNoteNum - clefLowestLine
    # The lowest volpiano note is 6 steps away from the lowest line
    index = distanceFromLowestLine + 6

    if index >= len(volpianoNotes):
        raise Exception(f'Cannot convert pitch {pitch.nameWithOctave} to volpiano: too high')
    elif index < 0:
        raise Exception(f'Cannot convert pitch {pitch.nameWithOctave} to volpiano: too low')
    
    if liquescence: 
        return volpianoLiquescents[index]
    else:
        return volpianoNotes[index]

class Chant21Object:
    """Base class for objects in Chant21. Most importantly, all those object can
    be exported to simple Python objects (dictionaries and lists), which in turn
    are directly serializable to JSON. Conversely, such objects can be used to
    recursively set the properties of a Chant21 object."""

    def __repr__(self):
        reprHead = '<'
        if self.__module__ != '__main__':
            reprHead += self.__module__ + '.'
        reprHead += self.__class__.__qualname__
        strRepr = self._reprInternal()
        if strRepr and not strRepr.startswith(':'):
            reprHead += ' '

        if strRepr:
            reprHead += strRepr.strip()
        return reprHead + '>'

    def _reprInternal(self) -> str:
        return ''

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

    def toObject(self, includeChildren : bool = True, 
        includeEditorial : bool = True, includeVolpiano : bool = False) -> dict:
        """Export the object to a plain Python dictionary. The returned object
        can have the following properties: 

        - ``type``: the name of the chant21 class, such as `'note'`
        - ``elements``: a list of dictionaries representing child elements
        - ``annotation``: annotations for the object
        - ``volpiano``: a volpiano string representing the object
        - ``editorial``: a dictionary with editorial information

        Specific classes will moreover add the properties necessary to fully 
        describe the object. The class :class:`Note` for example adds a 
        ``pitch`` property:

        >>> a = Note('A')
        >>> a.toObject()
        {'type': 'note', 'pitch': 'A'}
        >>> b = Note('B')
        >>> syll = Syllable()
        >>> syll.append(a)
        >>> syll.append(b)
        >>> syll.toObject()
        {'type': 'syllable', 'elements': [{'type': 'note', 'pitch': 'A'}, {'type': 'note', 'pitch': 'B'}]}
        
        Parameters
        ----------
        includeChildren : bool, optional
            Whether to include child objects, by default True. Children are 
            exported as a list in ``obj['elements']``.
        includeEditorial : bool, optional
            Whether to include editorial information, by default True. The
            editorial information is exported as ``obj['editorial']``.
        includeVolpiano : bool, optional
            Wether to include a Volpiano representation, by default False.
            The Volpiano version is exported as ``obj['volpiano']``.

        Returns
        -------
        dict
            A dictionary with at least a field ``type``, but possibly also
            ``editorial``, ``annotation``, ``volpiano`` and ``elements``.
        """
        obj = dict()
        obj['type'] = type(self).__name__.lower()

        if includeEditorial and self.hasEditorialInformation:
            obj['editorial'] = dict(self.editorial)
            # Remove annotation from editorial info, since that's already 
            # stored as the objects `annotation` property
            if 'annotation' in obj['editorial']:
                del obj['editorial']['annotation']
                if len(obj['editorial']) == 0:
                    del obj['editorial']
            
        if includeVolpiano and hasattr(self, 'volpiano'):
            obj['volpiano'] = self.volpiano

        if hasattr(self, 'annotation') and self.hasAnnotation:
            obj['annotation'] = self.annotation

        if includeChildren and hasattr(self, 'elements'):
            children = [el for el in self.elements if isinstance(el, Chant21Object)]
            kwargs = dict(includeEditorial=includeEditorial, 
                          includeVolpiano=includeVolpiano)
            obj['elements'] = [child.toObject(**kwargs) for child in children]

        return obj

    def fromObject(self, obj : dict, parent=None, parseChildren=True):
        """Set the properties of the current class instance using a dictionary
        of properties. The dictionary should be of the same form as the one 
        returned by  :meth:`chant.Chant21Object.toObject`. 

        >>> n = Note('C')
        >>> n.fromObject({'type': 'note', 'pitch': 'A4'})
        >>> n
        <chant21.chant.Note A>

        Parameters
        ----------
        obj : dict
            The object to import
        parent : Chant21Object, optional
            The parent object; this is set automatically when importing the 
            children, by default None.
        parseChildren : bool, optional
            Whether to also import the child objects, by default True
        """
        ownClassName = type(self).__name__.lower()
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

###

class Chant(Chant21Object, stream.Part):    
    
    def show(self, *args, makeFlatter=True, **kwargs):
        """Display the chant, as html or using the display options of music21.
        
        Chant21 allows you to visualize the structure of a chant interactively 
        in an IPython environment:

        .. jupyter-execute::

            from music21 import converter
            import chant21
            ch = converter.parse('cantus: 1---f-g--h---g--f--h---3/Abra cadabra')
            ch.show('html', showWords=True, showOptions=True)

        Optional keywords include ``showOptions``, ``showSections``, 
        ``showWords``, ``showSyllables``, ``showNeumes``, ``showMetadata`` 
        and ``showMisalignments``. See :func:`chant21.html.toWidget` for 
        more information.

        Parameters
        ----------
        how : string, optional
            How to display the chant? If ``'html'`` a HTML rendition of the 
            chant displayed, which only works in an IPython context. Otherwise
            the argument is passed to :meth:`music21.stream.Part.show`.
        makeFlatter : bool, optional
            Flatten the chant before showing it, by default True. This has no 
            effect when displaying as html.
        """
        if len(args) > 0 and args[0] == 'html':
            html = self.toHTML(**kwargs)
            try:
                from IPython.core.display import display, HTML
                return display(HTML(html))
            except:
                return html
        elif len(args) == 0 and makeFlatter:
            return self.flatter.show(makeFlatter=False, **kwargs)
        else:
            return super().show(*args, **kwargs)
    
    def toObject(self, **kwargs):
        """Export the object to a simple dictionary. See 
        :meth:`chant21.chant.Chant21Object.toObject`"""
        metadata = self.editorial.get('metadata', {})
        metadata['chant21version'] = __version__
        obj = {
            'type': 'chant',
            'metadata': metadata,
            'elements': [section.toObject(**kwargs) for section in self.sections]
        }
        if self.editorial:
            obj['editorial'] = { k: v for k, v in self.editorial.items() 
                if k != 'metadata'}
        return obj

    def fromObject(self, obj, **kwargs):
        """Set properties from a dictionary. 
        See :meth:`chant21.chant.Chant21Object.toObject`"""
        super().fromObject(obj, **kwargs)
        metadata = obj.get('metadata', {})
        self.editorial.metadata = metadata
    
    def toCHSON(self, fp=None, includeEditorial=True, **jsonKwargs):
        toObjectKwargs = dict(includeEditorial=includeEditorial)
        if fp is None:
            return json.dumps(self.toObject(**toObjectKwargs), **jsonKwargs)
        else:
            with open(fp, 'w') as handle:
                json.dump(self.toObject(**toObjectKwargs), handle, **jsonKwargs)
    
    def toHTML(self, filepath=None, chantOnly=True, **kwargs):
        """Export the chant to HTML and render the music in the Volpiano 
        typeface. There are two ways of exporting the chant: either a complete
        file is generated, with a title and metadata, or a 'widget' with only 
        the music is returned. The latter is used in Jupyter notebooks.

        Parameters
        ----------
        filepath : [type], optional
            If set the chant is exported to an HTML file, otherwise a HTML 
            string is returned, by default None
        chantOnly : bool, optional
            Create a widget with only the chant, not the title and additional
            metadata. By default True
        **kwargs : optional
            Optional keyword arguments for :func:`chant21.html.toFile` or
            :func:`chant21.html.toWidget`. Keywords include ``showOptions``,
            ``showSections``, ``showWords``, ``showSyllables``, ``showNeumes``,
            ``showMetadata`` and ``showMisalignments``.

        Returns
        -------
        str or none
            A html string if the html is not written to a file.
        """
        if filepath is not None or not chantOnly:
            return toFile(self, filepath=filepath, **kwargs)
        else:
            return toWidget(self, **kwargs)

    @property
    def flatter(self):
        """A copy of the chant where words, syllables and neumes have been
        flattened. It is not completely flat, since measures are preserved. 
        This method is useful for visualizing chants: ``ch.flatter.show()`` 
        will also show measures and barlines, where as ``ch.flat.show()`` will 
        not.

        >>> from music21 import converter
        >>> ch = converter.parse("(c4) A(dc~)B(c/e) (::) c(dc/fg) (::)", format='gabc')
        >>> ch.show('text')
        {0.0} <chant21.chant.Section>
            {0.0} <chant21.chant.Word>
                {0.0} <chant21.chant.Syllable>
                    {0.0} <music21.clef.Clef>
            {0.0} <chant21.chant.Word>
                {0.0} <chant21.chant.Syllable lyrics=A>
                    {0.0} <chant21.chant.Neume>
                        {0.0} <chant21.chant.Note D>
                        {1.0} <chant21.chant.Note C>
                {2.0} <chant21.chant.Syllable lyrics=B>
                    {0.0} <chant21.chant.Neume>
                        {0.0} <chant21.chant.Note C>
                    {1.0} <chant21.chant.Neume>
                        {0.0} <chant21.chant.Note E>
        {4.0} <chant21.chant.Section>
            {0.0} <chant21.chant.Word>
                {0.0} <chant21.chant.Syllable>
                    {0.0} <chant21.chant.PausaFinalis>
            {0.0} <chant21.chant.Word>
                {0.0} <chant21.chant.Syllable lyrics=c>
                    {0.0} <chant21.chant.Neume>
                        {0.0} <chant21.chant.Note D>
                        {1.0} <chant21.chant.Note C>
                    {2.0} <chant21.chant.Neume>
                        {0.0} <chant21.chant.Note F>
                        {1.0} <chant21.chant.Note G>
            {4.0} <chant21.chant.Word>
                {0.0} <chant21.chant.Syllable>
                    {0.0} <chant21.chant.PausaFinalis>
        >>> ch.flatter.show('text')
        {0.0} <music21.stream.Measure 0 offset=0.0>
            {0.0} <music21.clef.Clef>
            {0.0} <chant21.chant.Note D>
            {1.0} <chant21.chant.Note C>
            {2.0} <chant21.chant.Note C>
            {3.0} <chant21.chant.Note E>
            {4.0} <chant21.chant.PausaFinalis>
        {4.0} <music21.stream.Measure 0 offset=4.0>
            {0.0} <chant21.chant.Note D>
            {1.0} <chant21.chant.Note C>
            {2.0} <chant21.chant.Note F>
            {3.0} <chant21.chant.Note G>
            {4.0} <chant21.chant.PausaFinalis>
        """
        chant = deepcopy(self)
        elements = chant.flat
        chant.clear()
        curMeasure = stream.Measure()
        for element in elements:
            if isinstance(element, Pausa):
                if isinstance(element, bar.Barline):
                    curMeasure.rightBarline = element
                elif isinstance(element, articulations.BreathMark):
                    prevNote = element.previous(note.Note)
                    prevNote.articulations.append(element)
                    curMeasure.rightBarline = 'dotted'
                chant.append(curMeasure)
                curMeasure = stream.Measure()
            else:
                curMeasure.append(element)
        if len(curMeasure) > 0:
            chant.append(curMeasure)
        return chant

    @property
    def phrases(self):
        """music21.stream.Part: Returns all the phrases in a chant, where 
        phrases are all segments between two pausas. 
        
        Note that phrases are only reliable in GABC, and not in Cantus Volpiano.
        In gabc all pausa minima (breathing marks) are marked (by ``,``) and 
        reliable indicators of phrase boundaries. In Cantus Volpiano, pausa 
        minima however have a different meaning: they mark column or page 
        boundaries.
        
        >>> from music21 import converter
        >>> ch = converter.parse("(c4) A(dc)B(c,) C(dc) (::)", format='gabc')
        >>> ch.phrases.show('text') #doctest: +ELLIPSIS
        {0.0} <music21.stream.Stream 0x...>
            {0.0} <music21.clef.Clef>
            {0.0} <chant21.chant.Note D>
            {1.0} <chant21.chant.Note C>
            {2.0} <chant21.chant.Note C>
        {3.0} <music21.stream.Stream 0x...>
            {0.0} <chant21.chant.Note D>
            {1.0} <chant21.chant.Note C>

        """
        phrases = stream.Part()
        curPhrase = stream.Stream()
        for el in self.flat:
            if not isinstance(el, Pausa):
                curPhrase.append(el)
            else:
                phrases.append(curPhrase)
                curPhrase = stream.Stream()
        return phrases

    @property
    def sections(self):
        return self.getElementsByClass(Section)

    def addNeumeSlurs(self):
        """Add slurs over all notes that form a single neume.

        >>> from music21 import converter
        >>> ch = converter.parse('1---fgf-ga', format='cantus')
        >>> ch.flatter.show('text')
        {0.0} <music21.stream.Measure 0 offset=0.0>
            {0.0} <music21.clef.Clef>
            {0.0} <chant21.chant.Note F>
            {1.0} <chant21.chant.Note G>
            {2.0} <chant21.chant.Note F>
            {3.0} <chant21.chant.Note G>
            {4.0} <chant21.chant.Note A>
        >>> ch.addNeumeSlurs()
        >>> ch.flatter.show('text')
        {0.0} <music21.stream.Measure 0 offset=0.0>
            {0.0} <music21.clef.Clef>
            {0.0} <music21.spanner.Slur <chant21.chant.Note F><chant21.chant.Note G><chant21.chant.Note F>>
            {0.0} <chant21.chant.Note F>
            {1.0} <chant21.chant.Note G>
            {2.0} <chant21.chant.Note F>
            {3.0} <music21.spanner.Slur <chant21.chant.Note G><chant21.chant.Note A>>
            {3.0} <chant21.chant.Note G>
            {4.0} <chant21.chant.Note A>
        """
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
        self.insert(0, metadata.Metadata())
        if self.hasEditorialInformation and 'metadata' in self.editorial:
            meta = self.editorial.metadata
            if 'title' in meta:
                self.metadata.title = meta.get('title')
            elif 'name' in meta :
                self.metadata.title = meta.get('name')
            if 'transcriber' in meta:
                c = metadata.Contributor()
                c.name = meta['transcriber']
                c.role = 'transcriber'
                self.metadata.addContributor(c)
            
            #TODO add date
            # md.date = metadata.DateBetween(['2009/12/31', '2010/1/28'])
            #TODO add custom metadata fields: office part and mode

    def joinTextAcrossPausas(self):
        for section in self.sections:
            section.joinWordsAcrossPausas()

    # def addCantusText(self, text):
    #     visitor = VisitorCantusText(chant=self)
    #     visitParseTree(text, visitor)

class Section(Chant21Object, stream.Stream):
    _name = None

    @property
    def name(self):
        if self._name is not None:
            return self._name
        elif len(self.words) > 0 and self.words[0].hasAnnotation:
            annotation = self.words[0][0].annotation
            if annotation == 'V':
                return 'verse'
            elif annotation == 'R':
                return 'respond'
            elif annotation == 'A':
                return 'antiphon'
        return None
    
    @name.setter
    def name(self, name):
        self._name = name
            
    @property
    def words(self):
        return self.getElementsByClass(Word)
    
    def joinWordsAcrossPausas(self, joinSyllablesAcrossPausas=True):
        """Merge words containing pausas"""
        if len(self.words) == 1: return
        joinWords = False
        i = 1
        while i < len(self.words):
            prevWord, curWord = self.words[i-1:i+1]
            curWordIsBreathMark = isinstance(curWord.flat[0], articulations.BreathMark)
            curWordIsBarline = isinstance(curWord.flat[0], bar.Barline)
            
            if prevWord.hasLyrics and curWordIsBreathMark and not curWord.hasLyrics:
                joinWords = True
            if curWord.hasLyrics or curWordIsBarline:
                joinWords = False 

            if joinWords:
                prevWord.append(curWord.elements)
                self.remove(curWord)
            else:
                i += 1
        
        # Update syllables
        if joinSyllablesAcrossPausas:
            for word in self.words:
                word.joinSyllablesAcrossPausas()
                word.updateSyllableLyrics()

    def toObject(self, **kwargs):
        obj = super().toObject(**kwargs)
        if self.name is not None:
            obj['name'] = self.name
        return obj

class Word(Chant21Object, stream.Stream):

    musicAndTextAligned = None

    @property
    def syllables(self):
        return self.getElementsByClass(Syllable)
   
    @property
    def flatLyrics(self):
        try:
            return ''.join(syll.lyric for syll in self.syllables)
        except:
            return None
 
    @property
    def hasLyrics(self):
        if len(self.syllables) > 0:
            return self.syllables[0].hasLyrics
        else:
            return False

    @property
    def hasAnnotation(self):
        if len(self.syllables) > 0:
            return self.syllables[0].hasAnnotation
        else:
            return False

    def joinSyllablesAcrossPausas(self):
        """Merge syllables if they are separated by a syllable containing only a pausa.
        This is often the case on long melismas."""
        if len(self.syllables) == 1: return
        numSylls = len(self.syllables)
        joinSyllables = False
        i = 1
        while i < len(self.syllables):
            prevSyll, curSyll = self.syllables[i-1:i+1]
            curSyllIsBreathMark = isinstance(curSyll.flat[0], articulations.BreathMark)
            if prevSyll.hasLyrics and not curSyll.hasLyrics and curSyllIsBreathMark:
                joinSyllables = True
            if curSyll.hasLyrics:
                joinSyllables = False

            if joinSyllables:
                prevSyll.append(curSyll.elements)
                self.remove(curSyll)
            else:
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

    def toObject(self, **kwargs):
        obj = super().toObject(**kwargs)
        obj['musicAndTextAligned'] = self.musicAndTextAligned
        return obj
    
    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        self.updateSyllableLyrics()

class Syllable(Chant21Object, stream.Stream):
    
    def _reprInternal(self):
        if self.hasLyrics:
            return f'lyrics={self.lyric}'

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
    def hasLyrics(self):
        return self.lyric is not None

    @property
    def neumes(self):
        return self.getElementsByClass(Neume)

    def toObject(self, **kwargs):
        obj = super().toObject(**kwargs)
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

class Neume(Chant21Object, stream.Stream):
    def addSlur(self):
        """Adds a slur to the neumes notes"""
        notes = self.notes.elements
        if len(notes) > 1:
            slur = spanner.Slur(notes)
            slur.priority = -1
            self.insert(0, slur)
    
class Note(Chant21Object, note.Note):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.stemDirection = 'noStem'

    def _reprInternal(self):
        return self.name
    
    def toObject(self, **kwargs):
        obj = super().toObject(**kwargs)
        obj['pitch'] = self.pitch.nameWithOctave
        if self.notehead != 'normal':
            obj['notehead'] = self.notehead
        return obj

    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        self.pitch.nameWithOctave = obj['pitch']
        if 'notehead' in obj:
            self.notehead = obj['notehead']

    @property
    def volpiano(self):
        """A volpiano representation of the note"""
        return pitchToVolpiano(self.pitch, 
            liquescence=self.editorial.get('liquescence', False))

###

class Pausa(Chant21Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -1

class PausaMinima(Pausa, articulations.BreathMark):
    volpiano = '7'

class PausaMinor(Pausa, articulations.BreathMark):
    volpiano = '6'

class PausaMajor(Pausa, bar.Barline):
    volpiano = '3'

class PausaFinalis(Pausa, bar.Barline):
    volpiano = '4'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'light-light'

class Clef(Chant21Object, clef.TrebleClef):
    volpiano = '1'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = -2

###

class Alteration(Chant21Object, base.Music21Object):
    """Placeholder of the exact position of alterations in the chant.

    Alterations record the exact position of the alterations in the score,
    which is used when converting to other formats such as volpiano.
    Importantly, alterations are meaningless placeholder objects for music21.
    That means that alterations need not be *shown* in the exact same place 
    where we find them in the chant (i.e., the location of the Alteration 
    object). Music21 places accidentals according to a different logic, based
    on the pitches of the notes. However, the exact location of alterations 
    *is* preserved in the the HTLM rendition (using ``chant.show('html')``). 
    """ 
    
    pitch = None
    """music21.pitch.Pitch: the pitch at which the accidental is found in the
    score."""

    _volpianoNoteToAlteration = {}
    """dict: A dictionary mapping volpiano notes (e.g. ``b``) to the alteration
    at the same line (e.g. ``y``)."""

    def __init__(self, **kwargs):
        # Ensure that alterations always occur before their notes
        super().__init__(**kwargs)
        self.priority = -1

    def toObject(self, **kwargs):
        obj = super().toObject(**kwargs)
        obj['pitch'] = self.pitch.nameWithOctave
        return obj

    def fromObject(self, obj, **kwargs):
        super().fromObject(obj, **kwargs)
        self.pitch = pitch.Pitch(obj['pitch'])
        
    @property
    def volpiano(self):
        """str: a volpiano string representing the alteration."""
        volpiano = pitchToVolpiano(self.pitch)
        if not volpiano in self.volpianoNoteToAlteration:
            raise Exception('Accidental not supported')
        else:
            alteration = self._volpianoNoteToAlteration[volpiano]
            return alteration

class Flat(Alteration):
    """A placeholder class for flat signs. See :class:`Alteration` 
    for details."""
    _volpianoNoteToAlteration = {
        'b': 'y', # Low b-flat
        'j': 'i', # Middle b-flat
        'q': 'z', # High b-flat
        'e': 'w', # Low e-flat
        'm': 'x', # High e-flat
    }

class Natural(Alteration):
    """A placeholder class for natural signs. See :class:`Alteration` 
    for details."""
    _volpianoNoteToAlteration = {
        'b': 'Y', # Low b natural
        'j': 'I', # Middle b natural
        'q': 'Z', # High b natural
        'e': 'W', # Low e natural
        'm': 'X', # High e natural
    }

class Annotation(expressions.TextExpression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style.alignHorizontal = 'center'
        self.style.fontStyle = 'italic'
        # TODO this has no effect
        self.placement = 'above' 
        
### From music21 volpiano.py

class LineBreak(Chant21Object, base.Music21Object):
    '''
    Indicates that the line breaks at this point in the manuscript.
    Denoted by one 7.
    '''
    volpiano = '7'

class PageBreak(Chant21Object, base.Music21Object):
    '''
    Indicates that the page breaks at this point in the manuscript
    Denoted by two 7s.
    '''
    volpiano = '77'

class ColumnBreak(Chant21Object, base.Music21Object):
    '''
    Indicates that the page breaks at this point in the manuscript
    Denoted by three 7s.
    '''
    volpiano = '777'

class MissingPitches(Chant21Object, base.Music21Object):
    volpiano = '6------6'

##

CLASSES = {
    'chant': Chant,
    'section': Section,
    'word': Word,
    'syllable': Syllable,
    'neume': Neume,
    'note': Note,
    'clef': Clef,
    'pausa': Pausa,
    'pausaminima': PausaMinima,
    'pausaminor': PausaMinor,
    'pausamajor': PausaMajor,
    'pausafinalis': PausaFinalis,
    'annotation': Annotation,
    'alteration': Alteration,
    'flat': Flat,
    'natural': Natural
}
