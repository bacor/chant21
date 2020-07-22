from music21 import stream
from music21 import pitch
from music21 import note
from music21 import bar
from music21 import converter
from music21 import articulations

from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree as visitParseTree

from ..chant import Chant
from ..chant import Section
from ..chant import Note
from ..chant import Neume
from ..chant import Syllable
from ..chant import Word
from ..chant import Alteration
from ..chant import Pausa
from ..chant import Clef
# from ..chant import PausaMinima
# from ..chant import PausaMinor
from ..chant import PausaMajor
from ..chant import PausaFinalis
# from ..chant import Annotation
from ..chant import Natural
from ..chant import Flat
from ..chant import LineBreak
from ..chant import ColumnBreak
from ..chant import PageBreak
from ..chant import MissingPitches

from .parser_volpiano import ParserCantusVolpiano
from .parser_text import ParserCantusText
from .syllabifier import ChantSyllabifier
from .. import __version__

CHARACTERS = {
    'bars': '34567',
    'clefs': '12',
    'liquescents': '()ABCDEFGHJKLMNOPQRS',
    'naturals': 'IWXYZ',
    'notes': '89abcdefghjklmnopqrs',
    'flats': 'iwxyz',
    'alteration_positions': 'jembq',
    'spaces': '.,-',
    'others': "[]{¶",
}

def volpianoPositionToStep(position, clef, adjustClefOctave=0):
    positions = '89abcdefghjklmnopqrs'
    clefOctaves = dict(f=3, g=4)
    cPosition = dict(f='h', g='c')
    noteIndex = positions.index(position)
    cIndex = positions.index(cPosition[clef])
    stepsAboveC = noteIndex - cIndex
    octavesAboveC = stepsAboveC // 7
    noteName = 'CDEFGAB'[stepsAboveC % 7]
    noteOctave = clefOctaves[clef] + adjustClefOctave + octavesAboveC
    return f'{noteName}{noteOctave}'

class VisitorCantusVolpiano(PTNodeVisitor):
    
    def visit_volpiano(self, node, children):
        ch = Chant()
        curSection = Section()
        curClef = None
        ch.editorial.metadata = {
            'conversion': {
                'originalFormat': 'cantus/volpiano',
                'converter': 'chant21',
                'version': __version__
            }
        }

        for word in children: 
            # Ignore dashes at the very end of the chant
            if word == '-': continue
            curSection.append(word)
            
            # Scope of accidentals ends at word boundaries
            bIsFlat = False
            bIsNatural = False
            eIsFlat = False
            eIsNatural = False

            for el in word.flat:
                if isinstance(el, Note):
                    if curClef is None: 
                        raise MissingClef('Missing clef! Cannot process notes without a clef.')
                    position = el.editorial.volpianoPosition
                    stepWithOctave = volpianoPositionToStep(position, curClef)
                    el.nameWithOctave = stepWithOctave

                    if bIsNatural and el.step == 'B':
                        el.pitch.accidental = pitch.Accidental('natural')
                    elif eIsNatural and el.step == 'E':
                        el.pitch.accidental = pitch.Accidental('natural')
                    elif bIsFlat and el.step == 'B':
                        el.pitch.accidental = pitch.Accidental('flat')
                    elif eIsFlat and el.step == 'E':
                        el.pitch.accidental = pitch.Accidental('flat')
                
                elif isinstance(el, Alteration):
                    if curClef is None: 
                        raise MissingClef('Missing clef! Cannot process notes without a clef.')
                    position = el.editorial.volpianoPosition
                    stepWithOctave = volpianoPositionToStep(position, curClef)
                    el.pitch = pitch.Pitch(stepWithOctave)

                    # Reset alterations
                    bIsFlat = False
                    bIsNatural = False
                    eIsFlat = False
                    eIsNatural = False

                    # Update
                    if isinstance(el, Flat) and el.pitch.step == 'E':
                        eIsFlat = True
                    elif isinstance(el, Flat) and el.pitch.step == 'B':
                        bIsFlat = True
                    elif isinstance(el, Natural) and el.pitch.step == 'B':
                        bIsNatural = True
                    elif isinstance(el, Natural) and el.pitch.step == 'E':
                        eIsNatural = True
                    
                # Scope of accidentals ends at breathmarks
                elif isinstance(el, Pausa):
                    bIsFlat = False
                    bIsNatural = False
                    eIsFlat = False
                    eIsNatural = False  
                    
                    # Intermediate sections start (!) at pausa major (single barline)
                    # because annotations below them always refer to the next sections.
                    # The very last pausa finalis is part of the last section though
                    if isinstance(el, PausaMajor) or isinstance(el, PausaFinalis):
                        if not word == children[-1]:
                            curSection.remove(word)
                            ch.append(curSection)
                            curSection = Section()
                            curSection.append(word)
                        else:
                            ch.append(curSection)
                            curSection = Section()

                if isinstance(el, Clef):
                    volpiano = el.editorial.get('volpiano')
                    curClef = 'g' if volpiano == '1' else 'f'
        
        # Append cursection if this didn't happen yet: incipits for example
        # do not always contain a final barline
        if len(curSection) > len(ch):
            ch.append(curSection)

        return ch
    
    def visit_word(self, node, children):
        word = Word()
        for child in children:
            word.append(child)
        return word
    
    def visit_syllable(self, node, children):
        syllable = Syllable()
        for child in children:
            syllable.append(child)
        return syllable

    def visit_neume(self, node, children):
        neume = Neume()
        for child in children:
            neume.append(child)
        return neume
    
    def visit_note(self, node, children):
        n = Note()
        n.editorial.volpianoPosition = node.value
        return n

    def visit_liquescent(self, node, children):
        n = Note()
        noteIndex = CHARACTERS['liquescents'].index(node.value)
        n.editorial.volpianoPosition = CHARACTERS['notes'][noteIndex]
        n.editorial.liquescence = True
        n.notehead = 'x'
        return n

    def visit_clef(self, node, children):
        clef = Clef()
        clef.editorial.volpiano = node.value
        return clef

    def visit_alteration(self, node, children):
        if node.value in CHARACTERS['flats']:
            element = Flat()
            index = CHARACTERS['flats'].index(node.value)
        elif node.value in CHARACTERS['naturals']:
            element = Natural()
            index = CHARACTERS['naturals'].index(node.value)
        
        element.editorial.volpianoPosition = CHARACTERS['alteration_positions'][index]
        element.editorial.volpiano = node.value
        return element

    def visit_section_end(self, node, children):
        return PausaMajor()

    def visit_chant_end(self, node, children):
        return PausaFinalis()
    
    def visit_line_break(self, node, children):
        return LineBreak()
    
    def visit_column_break(self, node, children):
        return ColumnBreak()

    def visit_page_break(self, node, children):
        return PageBreak()

    def visit_missing_pitches(self, node, children):
        return MissingPitches()

###

TEXT_BARLINE = '|'
TEXT_SPACE = ' '

class VisitorCantusText(PTNodeVisitor):

    def __init__(self, chant, syllabifier, *args, strict=False, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.chant = chant
        self.syllabifier = syllabifier
        self.strict = strict
    
    def syllabify(self, text):
        """Syllabify Latin text using the syllabifier of the class."""
        return self.syllabifier.syllabify(text)

    def visit_text(self, node, children):
        txt_sections = [sec for sec in children 
            if type(sec) != str or sec != TEXT_BARLINE]
        mus_sections = self.chant

        #TODO change variables to camelcase!

        # Test if sections are alignable
        if self.strict and len(txt_sections) != len(mus_sections):
            raise SectionAlignmentError(
                f'The sections cannot be aligned: the text contains '
                f'{len(txt_sections)} sections, while the music contains '
                f'{len(mus_sections)} sections.'
            )
        elif not self.strict and len(txt_sections) != len(mus_sections):
            self.chant.editorial.misaligned = True

        # Align the sections
        for sec_num, (txt_section, mus_section) in enumerate(
            zip(txt_sections, mus_sections)):

            # Ignore words without notes: these cannot be aligned to text anyway
            mus_section_words = [w for w in mus_section if len(w.flat.notes) > 0]

            # Music is not aligned to text. Add lyrics to first syllable.
            if type(txt_section) == str:    
                l = note.Lyric(text=txt_section, applyRaw=True)
                l.syllabic = 'end'
                mus_section[0].editorial.unaligned = True
                mus_section[0][0].lyric = l
                continue
            
            # Check if the words in text and music are aligned
            if self.strict and len(txt_section) != len(mus_section_words):
                raise WordAlignmentError(
                    f'Section {sec_num} cannot be aligned. The text contains '
                    f'{len(txt_section)} words, whereas the music contains '
                    f'{len(mus_section_words)} words with notes.'
                )
            elif not self.strict and len(txt_section) != len(mus_section_words):
                mus_section.editorial.misaligned = True

            # Align the words in the section
            for word_num, (txt_word, mus_word) in enumerate(
                zip(txt_section, mus_section_words)):

                # Unaligned text
                if type(txt_word) == str:
                    l = note.Lyric(text=txt_word, applyRaw=True)
                    l.syllabic = 'end'
                    mus_word.editorial.unaligned = True
                    mus_word[0].lyric = l
                    continue
                    
                # Check if the syllables in text and music are aligned
                elif self.strict and len(txt_word) != len(mus_word):
                    raise SyllableAlignmentError(
                        f'Section {sec_num}, word {word_num} '
                        f'({"".join(txt_word)}) cannot be aligned. In the '
                        f'text, the word contains {len(txt_word)} '
                        f'syllables, but there are {len(mus_word)} '
                        f'syllables in the music.'
                    )
                elif not self.strict and len(txt_word) != len(mus_word):
                    mus_word.editorial.misaligned = True

                # Align the syllables of each word
                for syll_num, (txt_syll, mus_syll) in enumerate(
                    zip(txt_word, mus_word)):
                    # Add dashes to all but the final syllable
                    if syll_num < len(txt_word) - 1:
                        mus_syll.lyric = note.Lyric(text=f'{txt_syll}-')
                    else:
                        mus_syll.lyric = note.Lyric(txt_syll)

    def visit_section(self, node, children):
        words = children[0]
        return words

    def visit_tilda(self, node, children):
        return node.value.strip()

    def visit_words(self, node, children):
        return children

    def visit_word(self, node, children):
        syllables = self.syllabify(node.value)
        return syllables

    def visit_barline(self, node, children):
        return None

    def visit_space(self, node, children):
        return None

class TextAlignmentError(Exception):
    """General exception for all text-music alignment errors"""
    pass

class SectionAlignmentError(TextAlignmentError):
    """Exception raised when the number of sections in the music and text do not
    match"""
    pass

class WordAlignmentError(TextAlignmentError):
    """Exception for when the number of words in the music and text do not 
    match"""
    pass

class SyllableAlignmentError(TextAlignmentError):
    """Exception for when the number of syllables in the music and text do not 
    match"""
    pass

###

def addTextToChant(chant: Chant, text: str, strict: bool = False):
    """Parses the Cantus manuscript text and adds it as lyrics to a Chant 
    object.

    The text and music are not always aligned: sometimes the music might have
    more syllables than the text, or vice versa. This can be the result of 
    transcription errors or of faulty (automatic) syllabification. Misalignments
    are dealt with differently in strict and normal mode. In strict mode, 
    :class:`TextAlignmentError` exceptions are raised. In normal mode, 
    misalignments are only flagged in the editorial information, but otherwise 
    ignored. Misalignments are also highlighted in the HTML exports, which is 
    useful in Jupyter notebooks. 
    
    The following example illustrates the handling of misalignments hwne there 
    are more syllables in the music than in the text. Othe cases are similar.

    >>> from music21 import converter
    >>> ch = converter.parse('cantus: 1---a--b--c---d---3')
    >>> addTextToChant(ch, 'baca da', strict=True)
    Traceback (most recent call last):
    ...
    chant21.converter_cantus_volpiano.SyllableAlignmentError: Section 0, word 0 (baca) cannot be aligned. In the text, the word contains 2 syllables, but there are 3 syllables in the music.
    >>> addTextToChant(ch, 'baca da', strict=False)
    >>> word = ch[0][1]
    >>> word.editorial.misaligned
    True

    .. jupyter-execute::

        from music21 import converter
        import chant21
        ch = converter.parse('cantus: 1---a--b--c---d---3/baca da')
        ch.show('html', showOptions=False)

    Parameters
    ----------
    chant : Chant
        The chant object to which the text is to be added
    text : str
        The text, should be of the same form as the full_text_manuscript field
    strict : bool, optional
        When in strict mode, exceptions are raised whenever the music and text
        are misaligned (e.g. more syllables in the text than in the music).
        In normal mode such misalignments are accepted but flagged in the
        editorial information.
    """
    syllabifier = ChantSyllabifier()
    visitor = VisitorCantusText(chant, syllabifier, strict=strict)
    parser = ParserCantusText()
    parse = parser.parse(text)
    visitParseTree(parse, visitor)

def addCantusMetadataToChant(chant, data):
    chant.editorial.metadata.update(data.to_dict())

def convertCantusData(data, **kwargs):
    chant = converter.parse(data['volpiano'], format='cantus', **kwargs)
    if type(data['full_text_manuscript']) == str:
        addTextToChant(chant, data['full_text_manuscript'])
    elif type(data['incipit']) == str:
        addTextToChant(chant, data['incipit'])
    chant.editorial.metadata.update(data.to_dict())
    return chant

###

class ConverterCantusVolpiano(converter.subConverters.SubConverter):
    registerFormats = ('cantus', 'Cantus', 'CANTUS')
    registerInputExtensions = ('cantus', 'Cantus', 'CANTUS')
    
    def __init__(self, *args, strict=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.volpianoParser = ParserCantusVolpiano()
        self.volpianoVisitor = VisitorCantusVolpiano()
        self.strict = strict
    
    def parseData(self, strData, number=None):
        if '/' in strData:
            volpiano, text = strData.split('/')
        else:
            volpiano = strData
            text = None
        parse = self.volpianoParser.parse(volpiano, strict=self.strict)
        ch = visitParseTree(parse, self.volpianoVisitor)
        if text is not None:
            addTextToChant(ch, text, strict=self.strict)
        self.stream = ch

converter.registerSubconverter(ConverterCantusVolpiano)

class ConverterCantusVolpianoStrict(ConverterCantusVolpiano):
    registerFormats = ('cantus-strict', 'Cantus-strict', 'CANTUS-STRICT')
    registerInputExtensions = ('cantus-strict')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, strict=True, **kwargs)

converter.registerSubconverter(ConverterCantusVolpianoStrict)