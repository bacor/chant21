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
from .chant import PausaMinima
from .chant import PausaMinor
from .chant import PausaMajor
from .chant import PausaFinalis
from .chant import Annotation
from .chant import Natural
from .chant import Flat

from .parserGABC import ParserGABC

from . import __version__

NEUME_BOUNDARY = '_NEUME_BOUNDARY_'

class MissingClef(Exception):
    """Missing Clef Exception, raised when a clef is missing in the gabc"""
    pass

class AlterationWarning(Warning):
    """Exception raised when encountering an alteration at a step other than 
    B and E, which are not supported"""
    pass

def gabcPositionToStep(notePosition, clef, adjustClefOctave=0):
    """Convert a gabc note position to a step name"""
    positions = 'abcdefghijklm'
    cPosition = dict(c1='d', c2='f', c3='h', c4='j',
                      cb1='d', cb2='f', cb3='h', cb4='j', 
                      f1='a', f2='d', f3='e', f4='g')
    clefOctaves = dict(c1=4, c2=5, c3=5, c4=5,
                        cb1=4, cb2=5, cb3=5, cb4=5,
                        f1=4, f2=4, f3=4, f4=4)

    noteIndex = positions.index(notePosition.lower())
    cIndex = positions.index(cPosition[clef])
    stepsAboveC = noteIndex - cIndex
    octavesAboveC = stepsAboveC // 7
    noteName = 'CDEFGAB'[stepsAboveC % 7]
    noteOctave = clefOctaves[clef] + adjustClefOctave + octavesAboveC
    return f'{noteName}{noteOctave}'
    
def flatten(alist):
    """Flatten a list of lists"""
    return [item for sublist in alist for item in sublist]

###

class VisitorGABC(PTNodeVisitor):
    """Visiter class for converting a GABC parse tree to Music21"""
    
    def visit_file(self, node, children):
        if 'body' in children.results:
            ch = children.results['body'][0]
        else:
            ch = Chant()

        header = {
            'conversion': {
                'originalFormat': 'gabc',
                'converter': 'chant21',
                'version': __version__
            }
        }

        if 'header' in children.results:
            for headerSection in children.results['header']:
                header.update(headerSection)
        if len(header) > 0:
            ch.editorial.metadata = header

        return ch

    def visit_header(self, node, children):
        return { key: value for key, value in children }
    
    def visit_attribute(self, node, children):
        key = children.results['attribute_key'][0]
        value = children.results['attribute_value'][0]
        return key, value

    def visit_body(self, node, children):
        ch = Chant()
        curSection = Section()
        curClef = Clef()
        curGABCClef = None

        # First pass: add measurs
        for word in children:
            if not isinstance(word, Word): raise Exception('Quoi?')
            curSection.append(word)

            # Scope of accidentals ends with word boundaries
            curClefHasFlat = curGABCClef in ['cb1', 'cb2', 'cb3', 'cb4']
            bIsFlat = False or curClefHasFlat
            bIsNatural = False
            eIsFlat = False
            eIsNatural = False

            # Update the pitches of all notes based on the the clef
            # and accidentals
            for el in word.flat:
                if isinstance(el, note.Note):
                    if curGABCClef is None: 
                        raise MissingClef('Missing clef! Cannot process notes without a clef.')
                    position = el.editorial.gabcPosition
                    stepWithOctave = gabcPositionToStep(position, curGABCClef)
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
                    if curGABCClef is None: 
                        raise MissingClef('Cannot process notes without a clef.')
                    position = el.editorial.gabcPosition
                    step = gabcPositionToStep(position, curGABCClef)
                    el.pitch = pitch.Pitch(step)

                    # Reset alterations
                    bIsFlat = False or curClefHasFlat
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
                    bIsFlat = False or curClefHasFlat
                    bIsNatural = False
                    eIsFlat = False
                    eIsNatural = False  
                    
                    # Intermediate sections start (!) at pausa finalis (double barlines)
                    # because annotations below them always refer to the next sections.
                    # The very last pausa finalis is part of the last section though
                    if isinstance(el, PausaFinalis):
                        if not word == children[-1]:
                            curSection.remove(word)
                            ch.append(curSection)
                            curSection = Section()
                            curSection.append(word)
                        else:
                            ch.append(curSection)
                            curSection = Section()
                        
                elif isinstance(el, Clef):
                    curClef = el
                    curGABCClef = curClef.editorial.gabc
                elif isinstance(el, Annotation):
                    pass
                else:
                    raise Exception('Unknown element')
        
        if len(curSection.flat) > 0:
            ch.append(curSection)

        # ch.joinTextAcrossPausas()
        return ch
        
    def visit_word(self, node, children):
        word = Word()
        word.append(children)
        word.updateSyllableLyrics()
        return word

    def visit_syllable(self, node, children):
        elements = children.results.get('music', [[]])[0]
        syllable = Syllable()
        syllable.append(elements)
        
        if 'text' in children.results:
            for modifier in children.results.get('text')[0]:
                syllable = modifier(syllable)

        return syllable
        
    def visit_music(self, node, children):
        """Returns a list of elements"""
        elements = []
        curNeume = Neume()
        for element in children:
            # Notes are added to the current neume
            if isinstance(element, note.Note):
                curNeume.append(element)

                # End neumes on dots
                if 'gabcSuffixes' in element.editorial:
                    for suffix in element.editorial.gabcSuffixes:
                        if 'rhythmicSign' in suffix and suffix['rhythmicSign'] in ['.', '..']:
                            elements.append(curNeume)
                            curNeume = Neume()

            # Special symbols that are inserted outside Neumes
            elif (isinstance(element, Pausa) 
                or isinstance(element, Alteration)
                or isinstance(element, Clef)):
                if len(curNeume) > 0:
                    elements.append(curNeume)
                    curNeume = Neume()
                elements.append(element)

            # Close neumes on neume boundaries, ignore other spaces
            elif element is NEUME_BOUNDARY:
                if len(curNeume) > 0:
                    elements.append(curNeume)
                    curNeume = Neume()
            
            else:
                raise Exception('I dont know how to handle this')
        
        if len(curNeume) > 0: 
            elements.append(curNeume)
        return elements
    
    def visit_pausa(self, node, children):
        return children[0]
    
    def visit_pausa_finalis(self, node, children):
        el = PausaFinalis()
        el.editorial.gabc = node.value
        return el
    
    def visit_pausa_major(self, node, children):
        el = PausaMajor()
        el.editorial.gabc = node.value
        return el
    
    def visit_pausa_minor(self, node, children):
        el = PausaMinor()
        el.editorial.gabc = node.value
        return el
    
    def visit_pausa_minima(self, node, children):
        el = PausaMinima()
        el.editorial.gabc = node.value
        return el

    def visit_spacer(self, node, children):
        neumeBoundaries = ['/', '//', '/[-2]', '/[-1]', '/[0]', '/[1]', '/[2]', '/[3]', '/[4]']
        if node.value in neumeBoundaries:
            return NEUME_BOUNDARY
        else:
            return None

    def visit_clef(self, node, children):
        """Return a clef object with the gabc_clef stored as editorial info"""
        clef = Clef()
        clef.editorial.gabc = node.value
        return clef

    def visit_note(self, node, children):
        """Visit a note node and return a music21.note.Note instance. This
        will have the default pitch (C), and the gabc position is stored as
        editorial information. In the second pass the actual pitch is determined
        based on the current clef and accidentals.
        """
        n = Note()
        position = children.results.get('position')[0]
        n.editorial.gabcPosition = position
        n.editorial.gabcSuffixes = []

        # Suffix and prefix nodes return modifier functions that take a
        # music21.note.Note object as input and return a modified Note. In this
        # way we can add e.g. editorial information
        prefixes = children.results.get('prefix', [])
        suffixes = flatten(children.results.get('suffix', [[]]))
        modifiers = suffixes + prefixes
        for modify in modifiers:
            n = modify(n)

        if len(n.editorial.gabcSuffixes) == 0:
            del n.editorial['gabcSuffixes']

        return n

    def visit_position(self, node, children):
        return node.value

    def visit_prefix(self, node, children):
        """Return a modifier function that adds editorial information to the
        note to indicate it has a prefix and is liquescent"""
        def modifier(note):
            note.editorial.gabcPrefix = node.value
            note.editorial.liquescence = True
            note.notehead = 'x'
            return note

        return modifier
    
    def visit_suffix(self, node, children):
        """Visits suffix nodes. When children of suffix nodes are visited,
        a modifier function is returned that operates on music21.note.Note 
        objects. This suffix node returns a list of modifiers"""
        return children

    def visit_neume_shape(self, node, children):
        """Return a modifier function that writes the gabc note shape to the
        the music21.note.Note object"""
        def modifier(n):
            n.editorial.gabcSuffixes.append({'neumeShape': node.value})
            if node.value == 'w':
                n.notehead = 'x'
                n.editorial.liquescence = True
            return n

        return modifier
    
    def visit_rhythmic_sign(self, node, children):
        """Return a modifier function that writes the gabc rhythmic sign
        to the the music21.note.Note object"""
        def modifier(n):
            n.editorial.gabcSuffixes.append({'rhythmicSign': node.value})
            return n
        return modifier

    def visit_alteration(self, node, children):
        position = children.results.get('position')[0]
        alteration = node[1].value
        if alteration == 'x':
            element = Flat()
        elif alteration == 'y':
            element = Natural()
        else:
            raise AlterationWarning('Encountered a sharp. are not supported and ignored.')
        element.editorial.gabcPosition = position
        element.editorial.gabcAlteration = alteration
        return element

    # Text

    def visit_text(self, node, children):
        if 'annotation' in children.results:
            hasTextOutsideAnnotation = False
            for child in children:
                if type(child) == str and child.strip() != '':
                    hasTextOutsideAnnotation = True

            if hasTextOutsideAnnotation:
                def modifier(syll):
                    syll.annotation = node.flat_str()
                    syll.editorial.lyricsMayBeIncorrect = True
                    return syll
            else:
                modifier = children.results['annotation'][0]
        else:
            def modifier(syll):
                syll.lyric = children[0]
                return syll
        
        return [modifier]

    def visit_annotation(self, node, children):
        def modifier(syll):
            syll.annotation = children[0]
            syll.insert(0, Annotation(children[0]))
            return syll
        return modifier

    def visit_V(self, node, children):
        return 'V'

    def visit_R(self, node, children):
        return 'R'

    def visit_A(self, *args):
        return 'A'

    # Ignored properties
    
    def visit_empty_note_or_accent(self, node, children):
        if node.value in ['r', 'r0']:
            def modifier(n):
                n.editorial.gabcSuffixes.append({'emptyNote': node.value})
                n.noteheadFill = False
                return n
            return modifier
        else: 
            return None
    
    def visit_end_of_line(self, node, children):
        return None

    def visit_polyphony(self, node, children):
        """Polyphony is ignored, except for polyphonic alterations: 
        basically alterations printed on top of other notes"""
        if 'alteration' in children.results:
            return children.results.get('alteration')[0]
        else:
            return None

    def visit_brace(self, node, children):
        return None

    def visit_whitespace(self, node, children):
        return None

    def visit_macro(self, node, children):
        return None

    def visit_code(self, node, children):
        return None

    def visit_custos(self, node, children):
        return None

###

class ConverterGABC(converter.subConverters.SubConverter):
    registerFormats = ('gabc', 'GABC')
    registerInputExtensions = ('gabc', 'GABC')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = ParserGABC(root='file')
        self.visitor = VisitorGABC()

    def parseData(self, strData, number=None):
        parse = self.parser.parse(strData)
        ch = visitParseTree(parse, self.visitor)
        self.stream = ch

converter.registerSubconverter(ConverterGABC)