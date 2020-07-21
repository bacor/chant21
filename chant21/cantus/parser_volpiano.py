import re
import os.path
from arpeggio.cleanpeg import ParserPEG

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), 'cantus_volpiano.peg')

class ParserCantusVolpiano():
    
    def __init__(self, grammarPath = None, root: str = 'volpiano',
        strict: bool = False, **kwargs) -> None:
        """Initialize a Cantus Volpiano parser.

        Parameters
        ----------
        grammarPath : str, optional
            Path to the PEG grammar file, defaults to 
            ``grammars/cantus_volpiano.peg``
        root : str, optional
            Root element of the parser, by default 'volpiano'
        strict : bool, optional
            Whether to parse in strict mode or not. In strict mode, exceptions
            are raised whenever volpiano strings deviate from the standard 
            syntax. In non-strict mode, some deviations will be automatically 
            corrected. See :meth:`ParserCantusVolpiano.preprocess` for details.
            By default True
        **kwargs 
            Other keywords are passed to :class:`ParserPeg`.
        """
        if grammarPath == None:
            grammarPath = GRAMMAR_PATH
        if not os.path.exists(grammarPath):
            raise Exception(f'Grammar file ({ grammarPath }) does not exist')
        with open(grammarPath, 'r') as handle:
            grammar = handle.read()
        self.strict = strict
        self.parser = ParserPEG(grammar, root, skipws=False, **kwargs)

    def preprocess(self, volpiano: str, strict: bool = None):
        """Checks and possibly corrects the volpiano string before parsing. If 
        the parser operates in strict mode (``strict=True``) all deviations
        from the standard syntax result in parser exceptions. Otherwise, the
        preprocessor tries to correct common mistakes and variations.

        Volpiano should start with a clef:

        >>> parser = ParserCantusVolpiano(strict=False)
        >>> parser.preprocess('1---g')
        '1---g'
        >>> parser.preprocess('f-g')
        Traceback (most recent call last):
        ...
        chant21.parser_cantus_volpiano.ClefError: Missing clef: the volpiano does not start with a clef (1 or 2)

        Generally the clef should be followed by 3 hyphens. However, a number of 
        chants in Cantus use an alternative hyphenation where words appear to be
        separated by 2 hyphens, and syllables by 1. Chant21 will try to correct 
        this alternative hyphenation:

        >>> parser.preprocess('1--fg-f--h')
        '1---fg--f---h'
        
        Sometimes the clef suggests the alternative hyphenation (``1--f...``),
        but later in the chant we find a word boundary ``---``. In that case the
        clef hyphenation is corrected (or a HyphenationError is raised in strict
        mode):
        
        >>> parser.preprocess('1--f-g---h--f')
        '1---f-g---h--f'

        The use of 4 or 5 hyphens is not supported; those are replaced by a word
        boundary:

        >>> parser.preprocess('1---a----b-----c--d')
        '1---a---b---c--d'

        One situation where you may find more dashes is in the missing pitches
        fragment ``6------6``. When more than 6 hyphens are used between the 6s,
        those are removed:

        >>> parser.preprocess('1---6---------6')
        '1---6------6'

        Missing pitches often appear close to page breaks, and these are 
        marked directly before/after the missing pitches. There should be three
        hyphens before and after all that:

        >>> parser.preprocess('1---a--6------67--b')
        '1---a---6------67---b'

        Sometimes the wrong barlines are used: ``33`` instead of ``4`` for a 
        double barline; a thick barline ``5`` instead of the double barline 
        ``4``. Barlines should also be surrounded by 3 hyphens on both sides:

        >>> parser.preprocess('1---f-33-g')
        '1---f---4---g'
        >>> parser.preprocess('1---5')
        '1---4'
        
        Parameters
        ----------
        volpiano : str
            The volpianos tring
        strict : bool, optional
            Whether to operate in strict mode or not. In strict mode, exceptions
            are raised whenever volpiano strings deviate from the standard 
            syntax. In non-strict mode, some deviations will be automatically 
            corrected. The parameter defaults to the class' ``.strict`` 
            attribute.

        Returns
        -------
        str
            A preprocessed Volpiano string.

        Raises
        ------
        ClefError
            A missing clef
        HyphenationError
            Raised when there is a problem with the hyphenation.
        UnsupportedCharacterError
            Raised when the volpiano string contains non-volpiano characters.
        BarlineError
            Raised when for example the wrong barline symbols are used
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
        elif not has_standard_hyphenation:
            if strict:
                raise HyphenationError('Chant contains no word boundaries')
            else:
                volpiano = (volpiano.replace('--', '$$$')
                                    .replace('-', '--')
                                    .replace('$$$', '---'))

        # 4 or 5 hyphens are used as a separator: that's not supported. 
        # If not strict, replace by word boundary
        if re.match('.*[^-]-{4,5}[^-]', volpiano):
            if strict:
                raise HyphenationError('contains boundaries with 4 or 5 hyphens')
            else:
                def replacer(match):
                    return re.sub('-+', '---', match.group())
                volpiano = re.sub('[^-]-{4,5}[^-]', replacer, volpiano)
                # Repeat to also replace neighbouring matches
                volpiano = re.sub('[^-]-{4,5}[^-]', replacer, volpiano)
        
        # Missing pitches with more than 6 hyphens
        if re.match('.*6-{7,}6', volpiano):
            if strict:
                raise HyphenationError('Too many hyphens in missing pitches')
            else:
                volpiano = re.sub('6-{7,}6', '6------6', volpiano)

        # Missing pitches should be transcribed as ---6------6---: preceded 
        # and followed by a word boundary (3 hyphens)
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
        return volpiano

    def parse(self, volpiano: str, strict = None):
        """Parse a Cantus Volpiano string.

        >>> parser = ParserCantusVolpiano()
        >>> parse = parser.parse('1---a-b--c---d-e---4')
        >>> type(parse)
        <class 'arpeggio.NonTerminal'>

        Parameters
        ----------
        volpiano : str
            The volpiano string to be parsed
        strict : bool, optional
            Whether to parse in strict mode or not. In strict mode, exceptions
            are raised whenever volpiano strings deviate from the standard 
            syntax. In non-strict mode, some deviations will be automatically 
            corrected. See :meth:`ParserCantusVolpiano.preprocess` for details.
            By default True

        Returns
        -------
        arpeggio.NonTerminal
            The parse tree
        """
        volpiano = self.preprocess(volpiano, strict=strict)
        return self.parser.parse(volpiano)

class HyphenationError(Exception):
    pass

class BarlineError(Exception):
    pass

class UnsupportedCharacterError(Exception):
    pass

class ClefError(Exception):
    pass