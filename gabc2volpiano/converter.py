import json
from arpeggio import PTNodeVisitor
from arpeggio import visit_parse_tree
from gabc2volpiano.parser import GABCParser

OPTIONS = {
    
    # Volpiano constants
    # ------------------ 

    'volpiano_clef': '1',
    'volpiano_no_text': '',
    'volpiano_no_music': '.',
    'volpiano_music_neume_boundary': '-',
    'volpiano_text_syllable_boundary': '-',
    'volpiano_music_syllable_boundary': '--',
    'volpiano_text_word_boundary': ' ',
    'volpiano_music_word_boundary': '---',


    # GABC constants
    # --------------

    # GABC alterations that are actually converted to Volpiano.
    # Others (sharps) are ignored.
    'gabc_flat': 'x',
    'gabc_natural': 'y',


    # GABC to Volpiano conversion
    # ---------------------------

    # List of GABC neume shapes and prefixes that are converted to liquescents
    # Volpiano 2 might also support quilisma (but that adds other complications)
    'liquescent_neume_shapes': ['~'],
    'liquescent_prefixes': ['-'],

    # Map of GABC to volpiano spacers
    'spacers': {
        # No spaces
        '!': '',
        '@': '',
        # Neumatic-element boundaries
        '/': '-',
        '//': '-',
        '/[-2]': '-', # Is this even valid?
        '/[-1]': '-',
        '/[0]': '-',
        '/[1]': '-',
        '/[2]': '-',
        '/[3]': '-',
        '/[4]': '-', # Is this even valid?
        # Ignored
        ' ': ''
    },

    # Map of GABC to Volpiano barlines
    "barlines": {
        # Commas
        ",": "7",
        ",_": "7",
        ",0": "7",
        "'": "7",
        "`": "7",
        # Middle barline
        ";": "6",
        ";1": "6",
        ";2": "6",
        ";3": "6",
        ";4": "6",
        ";5": "6",
        ";6": "6",
        # Double barline
        "::": "4",
        # Barline
        ":": "3",
        ":?": "3"
    },


    # MIDI to Volpiano and GABC conversion
    # ------------------------------------

    # Map of midi keys to corresponding Volpiano flat signs
    # Note: midi keys are not the flats but the naturals 
    'midi_to_volpiano_flat': {
        59: "y", #B flat
        64: "w", #E flat
        71: "i", #B flat
        76: "x", #E flat
        83: "z", #B flat
    },

    # Map of midi keys to corresponding Volpiano natural signs
    'midi_to_volpiano_natural': {
        59: "Y", #B flat
        64: "W", #E flat
        71: "I", #B flat
        76: "X", #E flat
        83: "Z", #B flat
    },

    # Map of midi keys to volpiano notes
    'midi_to_volpiano_note': {
        53: "8", # F
        55: "9", # G
        57: "a",
        59: "b",
        60: "c",
        62: "d",
        64: "e",
        65: "f",
        67: "g",
        69: "h",
        71: "j",
        72: "k", # C
        74: "l",
        76: "m",
        77: "n",
        79: "o",
        81: "p",
        83: "q",
        84: "r", # C
        86: "s"
    },

    # Map of midi keys to volpiano liquescents
    'midi_to_volpiano_liquescent': {
        53: "(", # F
        55: ")", # G
        57: "A",
        59: "B",
        60: "C", # C
        62: "D",
        64: "E",
        65: "F",
        67: "G",
        69: "H",
        71: "J",
        72: "K", # C
        74: "L",
        76: "M",
        77: "N",
        79: "O",
        81: "P",
        83: "Q",
        84: "R", # C
        86: "S"
    },

    # Which midi key to use as the 'central' C in different clefs?
    # The default is midi key 60.
    'midi_c_per_clef': {
        'c4': 72,
        'c3': 72,
        'cb4': 72,
        'cb3': 72,
    },

    'ignore_unsupported_alterations': False,
}

####

def position_to_midi(position, clef, C=None):
    """Convert a note position (on the 4 lines) to a midi pitch"""
    positions = dict(a=-3, b=-2, c=-1, d=0, e=1, f=2, g=3, h=4, i=5, j=6, k=7, l=8, m=9)
    clef_position = dict(c1=0, c2=2, c3=4, cb3=4, c4=6, cb4=6, f3=1, f4=3)
    if C is None:
        C = OPTIONS['midi_c_per_clef'].get(clef, 60)
    if clef == 'cb3' or clef == 'cb4':
        scale = [0, 2, 4, 5, 7, 9, 10]
    else:
        scale = [0, 2, 4, 5, 7, 9, 11]

    # Position of the clef, wrt lowest line = 0
    clef_pos = clef_position[clef]
    pos = positions[position] - clef_pos

    # The midi pitch of the tonic below the note
    tonic_below = C + (pos // 7) * 12

    # Scale degree of the note in semitones, wrt tonic
    scale_degree = pos % 7
    semitones_above_tonic = scale[scale_degree]

    # Actual midi pitch
    midi = tonic_below + semitones_above_tonic

    return midi

def position_to_note(position, clef, C=None):
    midi = position_to_midi(position, clef, C=C)
    # When encountering B-flats in flat keys, return the note preceded by
    # an accidental. This is not optimal.
    # TODO find a better solution?
    if clef in ['cb3', 'cb4'] and midi in [58, 70, 82]: 
        midi += 1
        accidental = OPTIONS['midi_to_volpiano_flat'][midi]
        volpiano_note = OPTIONS['midi_to_volpiano_note'][midi]
        return accidental + volpiano_note
    else:
        volpiano_note = OPTIONS['midi_to_volpiano_note'][midi]
        return volpiano_note

def position_to_liquescent(position, clef, C=None):
    midi = position_to_midi(position, clef, C=C)
    # When encountering B-flats in flat keys, return the note preceded by
    # an accidental. This is not optimal.
    # TODO find a better solution?
    if clef in ['cb3', 'cb4'] and midi in [58, 70, 82]: 
        midi += 1
        accidental = OPTIONS['midi_to_volpiano_flat'][midi]
        volpiano_liquescent = OPTIONS['midi_to_volpiano_liquescent'][midi]
        return accidental + volpiano_liquescent
    else:
        volpiano_liquescent = OPTIONS['midi_to_volpiano_liquescent'][midi]
        return volpiano_liquescent

def position_to_flat(position, clef, C=None):
    midi = position_to_midi(position, clef, C=C)
    if midi not in OPTIONS['midi_to_volpiano_flat']:
        if OPTIONS['ignore_unsupported_alterations']:
            return False
        else:
            raise Warning(f'Volpiano has no flat at MIDI key {midi}. '
                         +'Is there a flat at the wrong line?')
    else:
        volpiano_flat = OPTIONS['midi_to_volpiano_flat'][midi]
        return volpiano_flat

def position_to_natural(position, clef, C=None):
    midi = position_to_midi(position, clef, C=C)
    if midi not in OPTIONS['midi_to_volpiano_natural']:
        if OPTIONS['ignore_unsupported_alterations']:
            raise Warning(f'Volpiano has no natural at MIDI key {midi}. '
                         +'Is there a natural at the wrong line?')
        else:
            return False
    else:
        volpiano_natural = OPTIONS['midi_to_volpiano_natural'][midi]
        return volpiano_natural

####

class VolpianoConverterVisitor(PTNodeVisitor):
    """Visiter class for converting a GABC parse tree to volpiano

    More precisely, it turns it into two things: (1) a string of text 
    (the lyrics) and (2) a list of musical events (notes, clefs, 
    barlines, etc.). The actual pitches of the notes can only be computed
    after the sequence of musical events has been collected, since they
    depend on the clef (special types of events). This post-processing
    step of turning note positions into actual pitches is *not* done by
    by this visitor class, but by the `VolpianoConverter` class. 

    Technically, events are objects with `type`, `value`, and/or `position`
    properties. For example:
    
    ```python
    note_event = {
        "type": "note"
        "position": "f"
    }
    barline_event = {
        "type": "barline"
        "value": "|"
    }
    ```
    """
    
    def visit_gabc_file(self, node, children):
        header = children.results['header'][0]
        text, music = children.results['body'][0]
        return header, text, music

    def visit_header(self, node, children):
        return { key: value for key, value in children }
    
    def visit_attribute(self, node, children):
        key = children.results['attribute_key'][0]
        value = children.results['attribute_value'][0]
        return key, value

    def visit_body(self, node, children):
        text = []
        music = []
        for i, (word_text, word_music) in enumerate(children):
            text.extend(word_text)
            music.extend(word_music)
            # Insert word boundaries between words
            if i < len(children) - 1:
                text.append(OPTIONS['volpiano_text_word_boundary'])
                event = dict(type='boundary', value=OPTIONS['volpiano_music_word_boundary'])
                music.append(event)

        return text, music

    def visit_word(self, node, children):
        text = []
        music = []
        for i, (syllable_text, syllable_music) in enumerate(children):
            text.append(syllable_text)
            music.extend(syllable_music)
            # Insert syllable boundaries *between* syllables (not at the end)
            if i < len(children) - 1:
                text.append(OPTIONS['volpiano_text_syllable_boundary'])
                event = dict(type='boundary', value=OPTIONS['volpiano_music_syllable_boundary'])
                music.append(event)
        return text, music

    def visit_whitespace(self, node, children):
        return None

    def visit_syllable(self, node, children):
        if 'music' in children.results:
            assert len(children.results['music']) == 1
            music = children.results['music'][0]
        else:
            event = {
                'type': 'no_music',
                'value': OPTIONS['volpiano_no_music']
            }
            music = [event]
        
        if 'text' in children.results:
            text = children.results['text'][0]
        else:
            text = OPTIONS['volpiano_no_text']

        return text, music

    def visit_music(self, node, children):
        """Returns a list of musical events (the children)
        
        Every event is an object with properties `type`, `value` and 
        possibly `position` (only for notes/alterations/liquescents)
        """

        return children

    def visit_barline(self, node, children):
        event = { 
            'type': 'barline',
            'value': OPTIONS['barlines'].get(node.value, '')
        }
        return event

    def visit_spacer(self, node, children):
        event = {
            'type': 'spacer',
            'value': OPTIONS['spacers'].get(node.value, '')
        }
        return event

    def visit_clef(self, node, children):
        event = {
            'type':'clef',
            'value': node.value
        }
        return event

    def visit_end_of_line(self, node, children):
        return None

    def visit_polyphony(self, node, children):
        return None

    def visit_brace(self, node, children):
        return None

    def visit_note(self, node, children):
        position = children.results.get('position')[0]
        is_liquescent = 'liquescent' in children
        is_flat = 'flat' in children
        is_natural = 'natural' in children

        if is_natural or is_flat:
            event = {
                'type': 'alteration',
                'position': position,
                'value': 'flat' if is_flat else 'natural'
            }
        elif is_liquescent:
            event = {
                'type': 'liquescent',
                'position': position
            }
        else:
            event = {
                'type': 'note',
                'position': position
            }

        return event

    def visit_position(self, node, children):
        return node.value.lower()

    def visit_prefix(self, node, children):
        if node.value in OPTIONS['liquescent_prefixes']:
            return 'liquescent'
        else:
            return None
    
    def visit_neume_shape(self, node, children):
        if node.value in OPTIONS['liquescent_neume_shapes']:
            return 'liquescent'
        else:
            return None
    
    def visit_alteration(self, node, children):
        if node.value == OPTIONS['gabc_flat']:
            return 'flat'
        elif node.value == OPTIONS['gabc_natural']:
            return 'natural'
        else:
            return None
        
    def visit_rhythmic_sign(self, node, children):
        # TODO Treat dots as neumatic cuts?
        return None
    
    def visit_empty_note_or_accent(self, node, children):
        return None

class VolpianoConverter:
    """GABC to Volpiano Converter

    This class converts GABC to Volpiano. There are two ways of doing this.
    Either you convert a full GABC file, using the `convert_file` function,
    or you convert the *body* of a GABC file, using the `convert` function.
    
    Technically, the clas first parses the GABC string,
    and then uses a visitor class to convert nodes to Volpiano --- nearly.
    It actually involves an intermediate step where all music is turned into
    a sequence of music events. This is done because the actual pitches depend
    on the clefs used (see the visitor docstring for details). The final 
    conversion to a volpiano string is done by this class.

    Attributes:
        parser (GABCParser): A parser for GABC strings (without header)
        file_parser (GABCParser): A parser for complete GABC files
        visitor (VolpianoConverterVisitor): the visitor doing most of the conversion

    Raises:
        MissingClef: when converting a GABC string without clef

    Todo:
        * Convert complete files
    """

    def __init__(self, **kwargs):
        self.parser = GABCParser(**kwargs, root='body')
        self.file_parser = GABCParser(**kwargs, root='gabc_file')
        self.visitor = VolpianoConverterVisitor()
    
    def _convert_music_events_to_volpiano(self, events: list):
        """Convert a sequence of music events into volpiano characters
        
        Args:
            events (list): List of events
        
        Raises:
            MissingClef: When a clef event is missing
        
        Returns:
            [string]: a volpiano string
        """
        volpiano = ''
        current_clef = None
        for event in events:

            # Clef
            if event['type'] == 'clef':
                current_clef = event['value']
                volpiano += OPTIONS['volpiano_clef']
            
             # Symbols independent of clef
            elif event['type'] in ['barline', 'boundary', 'spacer', 'no_music']:
                volpiano += event['value']

            # Symbols dependent on clef
            elif event['type'] in ['note', 'liquescent', 'alteration']:

                if current_clef is None:
                    raise MissingClef('Cannot determine the pitch of notes without clef')

                if event['type'] == 'liquescent':
                    liquescent = position_to_liquescent(
                        event['position'], current_clef)
                    volpiano += liquescent

                elif event['type'] == 'note':
                    note = position_to_note(
                        event['position'], current_clef)
                    volpiano += note
                
                elif event['type'] == 'alteration':
                    if event['value'] == 'flat':
                        alteration = position_to_flat(
                            event['position'], current_clef)
                    elif event['value'] == 'natural':
                        alteration = position_to_natural(
                            event['position'], current_clef)
                    
                    if alteration is not False:
                        volpiano += alteration
                    else:
                        # Ignore alterations other than B-flats/naturals 
                        # and E-flats/naturals
                        pass

        return volpiano

    def convert(self, gabc: str):
        """Convert a GABC string (without header) to Volpiano
        
        Args:
            gabc (string): The GABC (body) string (without header)
            
        Returns:
            [(string, string)]: text and volpiano
        """

        # Main conversion is done by the Visitor
        parse = self.parser.parse(gabc)
        text, music = visit_parse_tree(parse, self.visitor)

        # Second visit: convert positions to notes. 
        # We do not use the second_ mechanism of Arpeggio, since
        # visit_parse_tree does not return the second output
        volpiano = self._convert_music_events_to_volpiano(music)
        text = ''.join(text)
        return text, volpiano

    def convert_file_contents(self, gabc: str):
        """Converts the contents of a GABC file to Volpiano.

        A GABC file contains both a header and a body part, separated
        by `%%`.
        
        Args:
            gabc (string): The contents of a GABC file (including a header)
        
        Returns:
            A tuple `header, text, volpiano`. The `header` is a dictionary
            with all the information in the header of the GABC file. `text` 
            and `volpiano` are both strings.
        """
        # Main conversion is done by the Visitor
        parse = self.file_parser.parse(gabc)
        header, text, music = visit_parse_tree(parse, self.visitor)

        # Second visit: convert positions to notes. 
        # We do not use the second_ mechanism of Arpeggio, since
        # visit_parse_tree does not return the second output
        volpiano = self._convert_music_events_to_volpiano(music)
        text = ''.join(text)
        return header, text, volpiano

    def convert_file(self, source_fn: str, target_fn: str):
        """Convert a GABC file to a Volpiano JSON file.

        A Volpiano JSON file contains an object of the form:
        ```json
        {
            "metadata": { ... },
            "text": [string]
            "volpiano: [string]
        }
        ```

        Args:
            source_fn (string): the GABC source file
            target_fn (string): the Volpiano JSON target file
        """
        with open(source_fn, 'r') as handle:
            contents = handle.read()
            header, text, volpiano = self.convert_file_contents(contents)
        
        with open(target_fn, 'w') as handle:
            obj = dict(metadata=header, text=text, volpiano=volpiano)

            json.dump(obj, handle, indent=4)
        

####

class MissingClef(Exception):
    """Missing Clef Exception, raised when a clef is missing in the gabc"""
    pass
