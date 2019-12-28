from arpeggio.cleanpeg import ParserPEG
import os.path

grammar_fn = 'gabc.peg'
grammar_dir = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(grammar_dir, grammar_fn)
GRAMMAR_ROOT = 'gabc_file'

class GABCParser():
    """
    Class for parsing GABC (wrapper around an Arpeggio parser) 

    Attributes
    ----------
    parser : arpeggio.cleanpeg.ParserPEG
        The Arpeggio parser

    Methods
    -------
    parse(gabc)
        parses a gabc string
    parse_file(filename)
        parse the contents of a gabc file
    """

    def __init__(self, 
        grammar_path: str = GRAMMAR_PATH,
        root: str = GRAMMAR_ROOT,
        **kwargs) -> None:
        """
        Parameters
        ----------
        grammar_path : str, optional
            path to the grammar file (default is pygabc/gabc.peg)
        root : str, optional
            the root element of the parser (default is 'gabc_file')
        """
        
        if not os.path.exists(grammar_path):
            raise Exception(f'Grammar file ({ grammar_fn }) does not exist')

        with open(grammar_path, 'r') as handle:
            grammar = handle.read()
            
        self.parser = ParserPEG(grammar, root, skipws=False, **kwargs)

    def parse(self, gabc: str):
        """Parse a gabc string

        Parameters
        ----------
        gabc : str
            The gabc string to parse

        Returns
        -------
        arpeggio.NonTerminal
            The parse tree
        """
        
        return self.parser.parse(gabc)

    def parse_file(self, filename: str):
        """Parse a gabc file

        Parameters
        ----------
        filename : str
            The filename of the file to parse
    
        Raises
        ------
        FileNotFoundError
            If the passed filename does not exist

        Returns
        -------
        arpeggio.NonTerminal
            The parse tree
        """
        
        if not os.path.exists(filename):
            raise FileNotFoundError()

        with open(filename, 'r') as handle:
            contents = handle.read()
            return self.parse(contents)
