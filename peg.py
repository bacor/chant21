from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

# def file(): return ZeroOrMore(attribute), '%%\n', ZeroOrMore([syllable, '\n']), ZeroOrMore('\n'), EOF
def file(): return header, '%%\n'
def header(): return ZeroOrMore(attribute)
def body(): return ZeroOrMore([syllable, '\n']), ZeroOrMore('\n')

def attribute(): return attribute_key, ':', attribute_value, ';\n'
def attribute_key(): return _(r'[^:;]+')
def attribute_value(): return _(r'[^:;]+')

def clef(): return _(r'(c|f)[1-4]')
def barline(): return _(r",0|,_|,|'|`|::|:\?|:|;[1-6]|;")
def spacer(): return _(r'\!|@|//|/0|/\[-?[0-9]\]|/')

def note(): return ZeroOrMore(prefix), position, ZeroOrMore(suffix)
def prefix(): return ('-')
def suffix(): return _(r'~|>|<|v|V|o~|o<|o|w|s<|s|x|y|#|\.\.|\.|\'|_')
def position(): return _(r'[a-mA-M]')
def music(): return "(", ZeroOrMore([clef, note, barline, spacer]), ")"
def text(): return _(r'[^\(]+')
def syllable(): return (text, music)

parser = ParserPython(file)
myfile  = """
test:abc;
boe:12;
%%
asdfadf
"""
parser.parse(myfile)