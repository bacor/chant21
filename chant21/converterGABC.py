from music21 import stream
from music21 import pitch
from music21 import metadata
from music21 import note
from music21 import converter

from arpeggio import Terminal
from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree as visitParseTree

from .chant import Chant
from .chant import Note
from .chant import Neume
from .chant import Syllable
from .chant import Word
from .chant import Alteration
from .chant import Comma
from .chant import Barline
from .chant import Clef
from .chant import NoMusic
from .parserGABC import ParserGABC

OPTIONS = {
    'neume_boundaries': ['/', '//', '/[-2]', '/[-1]', '/[0]', '/[1]', '/[2]', '/[3]', '/[4]'],
    "commas": [",", ",_", ",0", "'", "`"],
    "middle_barlines": [";", ";1", ";2", ";3", ";4", ";5", ";6"],
    "double_barlines": ["::"],
    "barlines": [":", ":?"]
}

NEUME_BOUNDARY = '_NEUME_BOUNDARY_'

class MissingClef(Exception):
    """Missing Clef Exception, raised when a clef is missing in the gabc"""
    pass

def gabcPositionToStep(notePosition, clef, adjustClefOctave=0):
    """Convert a gabc note position to a step name"""
    positions = 'abcdefghijklm'
    cPosition = dict(c1='d', c2='f', c3='h', c4='j',
                      cb1='d', cb2='f', cb3='h', cb4='j', 
                      f1='a', f2='d', f3='e', f4='g')
    clefOctaves = dict(c1=4, c2=4, c3=5, c4=5,
                        cb1=4, cb2=4, cb3=5, cb4=5,
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

class GABCVisitor(PTNodeVisitor):
    """Visiter class for converting a GABC parse tree to Music21"""
    
    def visit_file(self, node, children):
        header = children.results.get('header', [{}])[0]
        ch = children.results.get('body', [Chant()])[0]
        
        ch.insert(0, metadata.Metadata())
        if 'title' in header:
            ch.metadata.title = header.get('title')

        for key, value in header.items():
            ch.editorial[key] = value
        return ch

    def visit_header(self, node, children):
        return { key: value for key, value in children }
    
    def visit_attribute(self, node, children):
        key = children.results['attribute_key'][0]
        value = children.results['attribute_value'][0]
        return key, value

    def visit_body(self, node, children):
        ch = Chant()
        curMeasure = stream.Measure()
        curClef = Clef()
        curGABCClef = None

        # First pass: add measurs
        for element in children:
            if isinstance(element, Word):
                curMeasure.append(element)

                # Scope of accidentals ends with word boundaries
                curClefHasFlat = curGABCClef in ['cb1', 'cb2', 'cb3', 'cb4']
                bIsFlat = False or curClefHasFlat
                bIsNatural = False
                eIsFlat = False
                eIsNatural = False

                # Update the pitches of all notes based on the the clef
                # and accidentals
                for el in element.flat:
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
                            raise MissingClef('Missing clef! Cannot process notes without a clef.')
                        position = el.editorial.gabcPosition
                        alteration = el.editorial.gabcAlteration
                        step = gabcPositionToStep(position, curGABCClef)[0]
                        
                        # Reset alterations
                        bIsFlat = False or curClefHasFlat
                        bIsNatural = False
                        eIsFlat = False
                        eIsNatural = False

                        # Update
                        if alteration == 'x' and step == 'E':
                            eIsFlat = True
                        elif alteration == 'x' and step == 'B':
                            bIsFlat = True
                        elif alteration == 'y' and step == 'B':
                            bIsNatural = True
                        elif alteration == 'y' and step == 'E':
                            eIsNatural = True
                        else:
                            raise Exception('Unsupported alteration')
                
                    # Scope of accidentals ends at breathmarks
                    if isinstance(el, Comma):
                        bIsFlat = False or curClefHasFlat
                        bIsNatural = False
                        eIsFlat = False
                        eIsNatural = False  
                    
            elif isinstance(element, Barline):
                # This also adds the element to the measure strem
                curMeasure.rightBarline = element
                ch.append(curMeasure)
                curMeasure = stream.Measure()
            elif isinstance(element, Clef):
                curClef = element
                curGABCClef = curClef.editorial.gabc
                curMeasure.append(element)
            elif isinstance(element, NoMusic):
                curMeasure.append(element)
            else:
                raise Exception('Unknown element')
        ch.append(curMeasure)
        return ch

    def visit_bar_or_clef(self, node, children):
        if 'clef' in children.results:
            element = children.results['clef'][0]
        elif 'barline' in children.results:
            element = children.results['barline'][0]
        else:
            element = NoMusic()
        element.text = children.results.get('text', [None])[0]
        return element
        
    def visit_word(self, node, children):
        word = Word()
        word.append(children)
        
        # Set syllable positions
        if len(word.syllables) == 1:
            word.syllables[0].lyrics[0].syllabic = 'single'
        elif len(word.syllables) > 1:
            for syll in word.syllables:
                syll.lyrics[0].syllabic = 'middle'
            word.syllables[0].lyrics[0].syllabic = 'begin'
            word.syllables[-1].lyrics[0].syllabic = 'end'

        return word

    def visit_syllable(self, node, children):
        text = children.results.get('text', [None])[0]
        elements = children.results.get('music', [[]])[0]
        syllable = Syllable()
        syllable.append(elements)
        syllable.text = note.Lyric(text=text, applyRaw=True)
        return syllable
        
    def visit_music(self, node, children):
        """Returns a list of elements"""
        elements = []
        curNeume = Neume()
        for element in children:
            # Notes are added to the current neume
            if isinstance(element, note.Note):
                curNeume.append(element)

            # Special symbols that are inserted outside Neumes
            elif type(element) in [Barline, Comma, Alteration]:
                if len(curNeume) > 0 and type(element) is Comma:
                    curNeume[-1].articulations = [element]
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
    
    def visit_barline(self, node, children):
        bar = Barline()
        bar.editorial.gabc = node.value
        return bar
    
    def visit_comma(self, node, children):
        comma = Comma()
        if len(children) == 3:
            # children is of the form [")(", ",", ")("]
            comma.editorial.gabc = children[1]
        else:
            comma.editorial.gabc = children[0]
        return comma

    def visit_spacer(self, node, children):
        if node.value in OPTIONS['neume_boundaries']:
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

        # Suffix and prefix nodes return modifier functions that take a
        # music21.note.Note object as input and return a modified Note. In this
        # way we can add e.g. editorial information
        prefixes = children.results.get('prefix', [])
        suffixes = flatten(children.results.get('suffix', [[]]))
        modifiers = suffixes + prefixes
        for modify in modifiers:
            n = modify(n)
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
            n.editorial.gabcShape = node.value
            if node.value == 'w':
                n.notehead = 'x'
                n.editorial.liquescence = True
            return n

        return modifier
    
    def visit_rhythmic_sign(self, node, children):
        """Return a modifier function that writes the gabc rhythmic sign
        to the the music21.note.Note object"""
        def modifier(n):
            n.editorial.gabcRhythmicSign = node.value
            return n
        return modifier

    def visit_alteration(self, node, children):
        position = children.results.get('position')[0]
        alteration = node[1].value
        element = Alteration()
        element.editorial.gabcPosition = position
        element.editorial.gabcAlteration = alteration
        return element

    # Ignored properties
    
    def _visit_empty_note_or_accent(self, node, children):
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

###

class ConverterGABC(converter.subConverters.SubConverter):
    registerFormats = ('gabc', 'GABC')
    registerInputExtensions = ('gabc', 'GABC')

    def __init__(self, *args, **kwargs):
        self.parser = ParserGABC(root='body')
        self.fileParser = ParserGABC(root='file')
        self.visitor = GABCVisitor()

    def parseData(self, strData, number=None):
        parse = self.fileParser.parse(strData)
        chant = visitParseTree(parse, self.visitor)
        self.stream = chant

converter.registerSubconverter(ConverterGABC)