from music21 import stream
from music21 import pitch
from music21 import note
from music21 import bar
from music21 import converter
from music21 import articulations
from pandas import isna

from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree as visitParseTree

from .chant import Chant
from .chant import Section
from .chant import Note
from .chant import Neume
from .chant import Syllable
from .chant import Word
from .chant import Alteration
from .chant import Pausa
from .chant import Clef
# from .chant import PausaMinima
# from .chant import PausaMinor
from .chant import PausaMajor
from .chant import PausaFinalis
# from .chant import Annotation
from .chant import Natural
from .chant import Flat
from .chant import LineBreak
from .chant import ColumnBreak
from .chant import PageBreak
from .chant import MissingPitches

from .parser_cantus_volpiano import ParserCantusVolpiano
from .parser_cantus_text import ParserCantusText
from .syllabifier import ChantSyllabifier
from . import __version__

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

def volpianoPositionToStep(position, clef, adjustClefOctave=-1):
    positions = '89abcdefghjklmnopqrs'
    clefOctaves = dict(f=4, g=5)
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

        # Store whether the chant uses incipit hyphenation
        ch.editorial.hasIncipitHyphenation = 'incipit' in children.results

        ch.editorial.metadata = {
            'conversion': {
                'originalFormat': 'cantus/volpiano',
                'converter': 'chant21',
                'version': __version__
            }
        }

        # First element is always a clef. For consistency wrap this in a 
        # syllable and a word object
        if isinstance(children[0][0], Clef):
            clef = children[0][0]
            volpiano = clef.editorial.get('volpiano')
            curClef = 'g' if volpiano == '1' else 'f'
            word = Word()
            syllable = Syllable()
            syllable.append(clef)
            word.append(syllable)
            curSection.append(word)

        words = children[0][1:]
        for word in words: 
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
                        if not word == words[-1]:
                            curSection.remove(word)
                            ch.append(curSection)
                            curSection = Section()
                            curSection.append(word)
                        else:
                            ch.append(curSection)
                            curSection = Section()

                if isinstance(el, Clef):
                    raise NotImplementedError()
                    # volpiano = el.editorial.get('volpiano')
                    # curClef = 'g' if volpiano == '1' else 'f'
        
        # Append cursection if this didn't happen yet: incipits for example
        # do not always contain a final barline
        if len(curSection) > len(ch):
            ch.append(curSection)

        return ch

    def visit_incipit(self, node, children):
        return children
    
    def visit_chant(self, node, children):
        return children
    
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

class VisitorCantusText(PTNodeVisitor):
    def __init__(self, chant, syllabifier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chant = chant
        self.syllabifier = syllabifier
    
    def syllabify(self, text):
        return self.syllabifier.syllabify(text)

    def visit_text(self, node, children):
        text_sections = [child for child in children 
            if type(child) != str or child != TEXT_BARLINE]
        for text_sec, chant_sec in zip(text_sections, self.chant):
            chant_words = [word for word in chant_sec if len(word.flat.notes) > 0]
            if type(text_sec) == str:
                # Music is not aligned to text. Add lyrics to first syllable.
                # TODO is there a more principled solution for this?
                l = note.Lyric(text=text_sec, applyRaw=True)
                l.syllabic = 'end'
                chant_words[0].musicAndTextAligned = False
                chant_words[0][0].lyric = l
            else:
                if self.chant.editorial.hasIncipitHyphenation:
                    text_words = [[syll for word in text_sec for syll in word]]
                else:
                    text_words = text_ec
                    # lyrics = []
                    # for word in text_words:
                    #     for i, syll in enumerate(word):
                    #         if i == len(word) - 1:
                    #             lyrics.append(note.Lyric(syll))
                    #         else:
                    #             lyrics.append(note.Lyric(f'{syll}-'))
                    # print(lyrics)
                    

                for text_word, chant_word in zip(text_words, chant_words):
                    for i, (text_syll, chant_syll) in enumerate(zip(text_word, chant_word)):
                        # Add dashes to all but the final syllable
                        if i < len(text_word) - 1:
                            chant_syll.lyric = note.Lyric(text=f'{text_syll}-')
                        else:
                            chant_syll.lyric = note.Lyric(text_syll)

    def visit_section(self, node, children):
        words = children[0]
        return words

    def visit_tilda(self, node, children):
        return node.value.strip()

    def visit_words(self, node, children):
        return [child for child in children if type(child) != str]

    def visit_word(self, node, children):
        syllables = self.syllabify(node.value)
        return syllables

    def visit_barline(self, node, children):
        return TEXT_BARLINE

###

def addTextToChant(chant, text):
    """Parses the Cantus manuscript text and adds it as lyrics to a Chant 
    object.

    Parameters
    ----------
    chant : chant21.chant.Chant
        The chant object to which the text is to be added
    text : str
        The text, should be of the same form as the full_text_manuscript field

    Returns
    -------
    chant21.chant.Chant
        the same chant object with added lyrics
    """
    syllabifier = ChantSyllabifier()
    visitor = VisitorCantusText(chant, syllabifier)
    parser = ParserCantusText()
    parse = parser.parse(text)
    visitParseTree(parse, visitor)
    return chant

def addCantusMetadataToChant(chant, data):
    chant.editorial.metadata.update(data.to_dict())

def convertCantusData(data):
    chant = converter.parse(data['volpiano'], format='cantus')
    if not isna(data['full_text_manuscript']):
        addTextToChant(chant, data['full_text_manuscript'])
    elif not isna(data['incipit']):
        addTextToChant(chant, data['incipit'])
    chant.editorial.metadata.update(data.to_dict())
    return chant

###

class ConverterCantusVolpiano(converter.subConverters.SubConverter):
    registerFormats = ('cantus', 'Cantus', 'CANTUS')
    registerInputExtensions = ('cantus', 'Cantus', 'CANTUS')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.volpianoParser = ParserCantusVolpiano()
        self.volpianoVisitor = VisitorCantusVolpiano()
    
    def parseData(self, strData, number=None, strict = False):
        if '/' in strData:
            volpiano, text = strData.split('/')
        else:
            volpiano = strData
            text = None
        parse = self.volpianoParser.parse(volpiano, strict = strict)
        ch = visitParseTree(parse, self.volpianoVisitor)
        if text is not None:
            addTextToChant(ch, text)
        self.stream = ch

converter.registerSubconverter(ConverterCantusVolpiano)