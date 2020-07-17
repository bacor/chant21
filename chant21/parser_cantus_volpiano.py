from arpeggio.cleanpeg import ParserPEG
import os.path
import re

cur_dir = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(cur_dir, 'grammars', 'cantus_volpiano.peg')
GRAMMAR_ROOT = 'volpiano'

class ParserCantusVolpiano():
    """
    Class for parsing Volpiano

    Attributes:
        parser (arpeggio.cleanpeg.ParserPEG): The Arpeggio parser
    """

    def __init__(self, 
        grammar_path: str = GRAMMAR_PATH,
        root: str = GRAMMAR_ROOT,
        strict: bool = True,
        **kwargs) -> None:
        """
        Args:
            grammar_path (:obj:`str`, optional): path to the grammar file 
                (default is pygabc/gabc.peg)
            root (:obj:`str`, optional): the root element of the parser 
                (default is 'gabc_file')
        """
        if not os.path.exists(grammar_path):
            raise Exception(f'Grammar file ({ grammar_path }) does not exist')

        with open(grammar_path, 'r') as handle:
            grammar = handle.read()
        
        self.strict = strict
        self.parser = ParserPEG(grammar, root, skipws=False, **kwargs)

    def parse(self, volpiano: str, debug: bool = True, strict = None):
        """Parse a volpiano string

        Args:
            volpiano (str): The volpiano string to parse

        Returns:
            arpeggio.NonTerminal: The parse tree
        """
        if strict is None: strict = self.strict

        if volpiano[0] not in '12':
            raise ClefError('Missing clef: the volpiano does not start with a clef (1 or 2)')
        
        if re.match('^[12]-?[^-]', volpiano):
            raise HyphenationError('Invalid clef hyphenation: chant should start with 1-- or 1---')
        
        # Mixed hyphenation: start with 1-- (2 hyphens), but still contains word 
        # boundaries (3 hyphens). 
        has_standard_hyphenation = volpiano.startswith('1---') or volpiano.startswith('2---')
        if not has_standard_hyphenation and re.match('.*[^-]---[^-]', volpiano):
            if strict:
                raise HyphenationError('Mixed hyphenation: starts with 1--, but contains word boundaries')
            else:
                # Todo debug
                volpiano = volpiano[0] + '---' + volpiano[3:]

        # 4 or 5 hyphens are used as a separator: that's not supported. 
        # If not strict, replace by word boundary
        if re.match('.*[^-]-{4,5}[^-]', volpiano):
            if strict:
                raise HyphenationError('contains boundaries with 4 or 5 hyphens')
            else:
                def replacer(match):
                    return re.sub('-+', '---', match.group())
                volpiano = re.sub('[^-]-{4,5}[^-]', replacer, volpiano)
        
        # Missing pitches with more than 6 hyphens
        if re.match('.*6-{7,}6', volpiano):
            if strict:
                raise HyphenationError('Too many hyphens in missing pitches')
            else:
                volpiano = re.sub('6-{7,}6', '6------6', volpiano)

        # Missing pitches should be transcribed as ---6------6---: preceded and followed
        # by a word boundary (3 hyphens)
        if re.match('.*[^-]--7*6------6', volpiano) or re.match('.*6------67*--[^-]', volpiano):
            if strict:
                raise HyphenationError('Missing pitches preceded/followed by syllable boundary')
            else:
                def replacer(match):
                    vol = match.group()
                    if vol[2] != '-': vol = '-' + vol
                    if vol[-3] != '-': vol += '-'
                    return vol
                volpiano = re.sub('-+7*6------67*-+', replacer, volpiano)

        if '.' in volpiano:
            if strict:
                raise UnsupportedCharacterError('The dot (.) is not supported, use hyphens instead.')
            else:
                volpiano = volpiano.replace('.', '')

        # Double barlines written as '33' (two single barlines) rather than 4
        if '33' in volpiano:
            if strict:
                raise BarlineError('Use "4" for a double barline, not "33"')
            else:
                volpiano = volpiano.replace('33', '4')

        # Thick barlines are not used.
        if '5' in volpiano:
            if strict:
                raise BarlineError('Use "4" for a double barline, not "5"')
            else:
                volpiano = volpiano.replace('5', '4')

        # Barlines preceded by too few hyphens
        if has_standard_hyphenation and re.match('.*[^-]-{1,2}[34]', volpiano):
            if strict:
                raise HyphenationError('Barlines should be preceded by 3 hyphens')
            else:
                def replacer(match):
                    vol = match.group()
                    return vol[0] + '---' + vol[-1]
                volpiano = re.sub('[^-]-{1,2}[34]', replacer, volpiano)

        # Barlines followed by too few hyphens
        if has_standard_hyphenation and re.match('.*[34]-{1,2}[^-]', volpiano):
            if strict:
                raise HyphenationError('Barlines should be followed by 3 hyphens')
            else:
                def replacer(match):
                    vol = match.group()
                    return vol[0] + '---' + vol[-1]
                volpiano = re.sub('[34]-{1,2}[^-]', replacer, volpiano)

        # TODO the same problem occurs for non-standard hyphenation. Perhaps add this?

        return self.parser.parse(volpiano)

class HyphenationError(Exception):
    pass

class BarlineError(Exception):
    pass

class UnsupportedCharacterError(Exception):
    pass

class ClefError(Exception):
    pass