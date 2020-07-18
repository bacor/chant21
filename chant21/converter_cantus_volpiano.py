from music21 import stream
from music21 import pitch
from music21 import note
from music21 import bar
from music21 import converter
from music21 import articulations

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
# from . import __version__

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

    # def visit_other(self, node, children):
    #     word = Word()
    #     for child in children:
    #         word.append(child)
    #     return word
    
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

class ConverterCantusVolpiano(converter.subConverters.SubConverter):
    registerFormats = ('cantus', 'Cantus', 'CANTUS')
    registerInputExtensions = ('cantus', 'Cantus', 'CANTUS')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = ParserCantusVolpiano()
        self.visitor = VisitorCantusVolpiano()
    
    def parseData(self, strData, number=None, strict = False):
        parse = self.parser.parse(strData, strict = strict)
        ch = visitParseTree(parse, self.visitor)
        self.stream = ch

converter.registerSubconverter(ConverterCantusVolpiano)