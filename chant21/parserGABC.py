from arpeggio.cleanpeg import ParserPEG
import os.path

grammarFn = 'gabc.peg'
grammarDir = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(grammarDir, grammarFn)

class ParserGABC():
    """
    Class for parsing GABC (wrapper around an Arpeggio parser) 

    Attributes:
        parser (arpeggio.cleanpeg.ParserPEG): The Arpeggio parser
    """

    def __init__(self, 
        grammarPath: str = GRAMMAR_PATH,
        root: str = 'file',
        **kwargs) -> None:
        """
        Args:
            grammar_path (:obj:`str`, optional): path to the grammar file 
                (default is pygabc/gabc.peg)
            root (:obj:`str`, optional): the root element of the parser 
                (default is 'gabc_file')
        """
        if not os.path.exists(grammarPath):
            raise Exception(f'Grammar file ({ grammarFn }) does not exist')

        with open(grammarPath, 'r') as handle:
            grammar = handle.read()
            
        self.parser = ParserPEG(grammar, root, skipws=False, memoization=True, **kwargs)

    def parse(self, gabc: str, debug=False):
        """Parse a gabc string

        Args:
            gabc (str): The gabc string to parse

        Returns:
            arpeggio.NonTerminal: The parse tree
        """
        _debug = self.parser.debug
        self.parser.debug = debug or _debug
        parse = self.parser.parse(gabc)

        if type(parse) == list and len(parse) == 0 and len(gabc) > 0:
            raise EmptyParseError()
        if parse.position_end < len(gabc):
            raise IncompleteParseError(f'Parsing ended at position {parse.position_end} (input length {len(gabc)})')
        
        self.parser.debug = _debug
        return parse

    def parseFile(self, filename: str):
        """Parse a gabc file

        Args:
            filename (str): The filename of the file to parse
    
        Raises:
            FileNotFoundError: If the passed filename does not exist

        Returns:
            arpeggio.NonTerminal: The parse tree
        """
        
        if not os.path.exists(filename):
            raise FileNotFoundError()

        with open(filename, 'r') as handle:
            contents = handle.read()
            return self.parse(contents)

class IncompleteParseError(Exception):
    pass


class EmptyParseError(Exception):
    pass