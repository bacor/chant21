import re
import os.path
from arpeggio.cleanpeg import ParserPEG

GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), 'cantus_text.peg')

class ParserCantusText():

    def __init__(self, grammarPath: str = GRAMMAR_PATH, root: str = 'text',
        **kwargs) -> None:
        """Initialize a Cantus Text parser.

        Parameters
        ----------
        grammarPath : str, optional
            Path to the PEG grammar file, defaults to 
            ``cantus/cantus_text.peg``
        root : str, optional
            Root element of the parser, by default 'text'
        **kwargs 
            Other keywords are passed to :class:`ParserPeg`.
        """
        if not os.path.exists(grammarPath):
            raise Exception(f'Grammar file ({ grammarPath }) does not exist')
        with open(grammarPath, 'r') as handle:
            grammar = handle.read()        
        self.parser = ParserPEG(grammar, root, skipws=False, **kwargs)

    def parse(self, text: str, debug: bool = True):
        # TODO docstring
        if not type(text) == str: return None
        return self.parser.parse(text)