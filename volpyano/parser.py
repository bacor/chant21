from arpeggio.cleanpeg import ParserPEG
import os.path

grammar_fn = 'volpiano.peg'
grammar_dir = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(grammar_dir, grammar_fn)
GRAMMAR_ROOT = 'volpiano_file'

class VolpianoParser():
    """
    Class for parsing Volpiano

    Attributes:
        parser (arpeggio.cleanpeg.ParserPEG): The Arpeggio parser
    """

    def __init__(self, 
        grammar_path: str = GRAMMAR_PATH,
        root: str = GRAMMAR_ROOT,
        **kwargs) -> None:
        """
        Args:
            grammar_path (:obj:`str`, optional): path to the grammar file 
                (default is pygabc/gabc.peg)
            root (:obj:`str`, optional): the root element of the parser 
                (default is 'gabc_file')
        """
        if not os.path.exists(grammar_path):
            raise Exception(f'Grammar file ({ grammar_fn }) does not exist')

        with open(grammar_path, 'r') as handle:
            grammar = handle.read()
            
        self.parser = ParserPEG(grammar, root, skipws=False, **kwargs)

    def parse(self, volpiano: str):
        """Parse a volpiano string

        Args:
            volpiano (str): The volpiano string to parse

        Returns:
            arpeggio.NonTerminal: The parse tree
        """
        return self.parser.parse(volpiano)
