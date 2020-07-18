from arpeggio.cleanpeg import ParserPEG
import os.path
import re
from pandas import isna

cur_dir = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(cur_dir, 'grammars', 'cantus_text.peg')
GRAMMAR_ROOT = 'text'

class ParserCantusText():
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

    def parse(self, text: str, debug: bool = True, strict = None):
        if isna(text): return None
        if strict is None: strict = self.strict 
        return self.parser.parse(text)
