from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _
from arpeggio import ParserPython

# def file(): return ZeroOrMore(attribute), '%%\n', ZeroOrMore([syllable, '\n']), ZeroOrMore('\n'), EOF
def gabc_file(): return header, '%%\n', EOF


# Header with metadata
def header(): return ZeroOrMore(attribute)
def attribute(): return (attribute_key, ':', attribute_value, ';\n')
def attribute_key(): return _(r'[^:;]+')
def attribute_value(): return _(r'[^:;]+')


def body(): return _(r'.*')

# Musical expressions
def music(): return ZeroOrMore([clef, note, barline, spacer])
def clef(): return _(r'(c|f)[1-4]')
def barline(): return _(r",0|,_|,|'|`|::|:\?|:|;[1-6]|;")
def spacer(): return _(r'\!|@|//|/0|/\[-?[0-9]\]|/')

## NOTES

def note(): return ZeroOrMore(prefix), position, ZeroOrMore(suffix)

# Prefix, basically only a -
def prefix(): return '-'

# Suffixes
def suffix(): return (
    Optional(neume_shape), 
    Optional(alteration), 
    Optional(rhythmic_sign), 
    ZeroOrMore(empty_note_or_accent))
def position(): return _(r'[a-mA-M]')
def neume_shape(): return _(r'~|>|<|v|V|o(~|<)?|w|s<?')
def alteration(): return _(r'x|y|#')
def rhythmic_sign(): return _(r'\.\.?|\'(0|1)?|_[0-5]*')
# TODO: types of rhythmic signs? E.g. episema, etc? 
def empty_note_or_accent(): return _(r'r[0-5]?|R')

# def text(): return _(r'[^\(]+')
# def syllable(): return (text, music)

# parser = ParserPython(gabc_file, debug=True)
# myfile  = """test:hhoi;
# boe:12;
# %%
# """
# # print(myfile)
# parse = parser.parse(myfile)
# print(parse)

def test_header_parser():
    header_parser = ParserPython(header)
    gabc_str = """foo:2;
    bar:test(123);
    """
    parse = header_parser.parse(gabc_str)
    assert parse[0].attribute_key.value == 'foo'
    assert parse[0].attribute_value.value == '2'
    assert parse[1].attribute_key.value == 'bar'
    assert parse[1].attribute_value.value == 'test(123)'

def test_one_note_neumes():
    parser = ParserPython(note)

    # Test single suffix
    parse = parser.parse('G~')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'G'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == '~'
    assert parse[1][0].rule_name == 'neume_shape'

    # Test two-character suffix
    parse = parser.parse('Go~')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'G'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == 'o~'
    assert parse[1][0].rule_name == 'neume_shape'

    parse = parser.parse('Go')
    assert parse[1].value == 'o'
    assert parse[1][0].rule_name == 'neume_shape'

    parse = parser.parse('Go<')
    assert parse[1].value == 'o<'
    assert parse[1][0].rule_name == 'neume_shape'

    parse = parser.parse('Gs')
    assert parse[1].value == 's'
    assert parse[1][0].rule_name == 'neume_shape'

    parse = parser.parse('Gs<')
    assert parse[1].value == 's<'
    assert parse[1][0].rule_name == 'neume_shape'

def test_alterations():
    parser = ParserPython(note)
    parse = parser.parse('gx')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'g'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == 'x'
    assert parse[1][0].rule_name == 'alteration'

    parse = parser.parse('gy')
    assert parse[1].value == 'y'
    assert parse[1][0].rule_name == 'alteration'

    parse = parser.parse('g#')
    assert parse[1].value == '#'
    assert parse[1][0].rule_name == 'alteration'

def test_rhythmic_signs():
    parser = ParserPython(note)
    
    parse = parser.parse('g_')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'g'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == '_'
    assert parse[1][0].rule_name == 'rhythmic_sign'

    parse = parser.parse('g..')
    assert parse[1].value == '..'
    assert parse[1][0].rule_name == 'rhythmic_sign'

    parse = parser.parse('g..')
    assert parse[1].value == '..'
    assert parse[1][0].rule_name == 'rhythmic_sign'

    parse = parser.parse("g'")
    assert parse[1].value == "'"
    assert parse[1][0].rule_name == 'rhythmic_sign'

    parse = parser.parse("g'1")
    assert parse[1].value == "'1"
    assert parse[1][0].rule_name == 'rhythmic_sign'

    parse = parser.parse('H_502')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'H'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == '_502'
    
def test_empty_notes():
    parser = ParserPython(note)
    parse = parser.parse('gr')
    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'g'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == 'r'
    assert parse[1][0].rule_name == 'empty_note_or_accent'

    parse = parser.parse("gR")
    assert parse[1].value == "R"
    assert parse[1][0].rule_name == 'empty_note_or_accent'

    parse = parser.parse("gr0")
    assert parse[1].value == "r0"
    assert parse[1][0].rule_name == 'empty_note_or_accent'

def test_accents():
    parser = ParserPython(note)
    parse = parser.parse('gr1')

    assert parse[0].rule_name == 'position'
    assert parse[0].value == 'g'
    assert parse[1].rule_name == 'suffix'
    assert parse[1].value == 'r1'
    assert parse[1][0].rule_name == 'empty_note_or_accent'

    parse = parser.parse("gr2")
    assert parse[1].value == "r2"
    assert parse[1][0].rule_name == 'empty_note_or_accent'
    
    parse = parser.parse("gr3")
    assert parse[1].value == "r3"
    assert parse[1][0].rule_name == 'empty_note_or_accent'
    
    parse = parser.parse("gr4")
    assert parse[1].value == "r4"
    assert parse[1][0].rule_name == 'empty_note_or_accent'

    parse = parser.parse("gr5")
    assert parse[1].value == "r5"
    assert parse[1][0].rule_name == 'empty_note_or_accent'

    # Multiple 
    parse = parser.parse("gr0r3")
    assert parse[1].rule_name == 'suffix'
    assert parse[1][0].rule_name == 'empty_note_or_accent'
    assert parse[1][0].value == "r0"
    assert parse[1][0].rule_name == 'empty_note_or_accent'
    assert parse[1][1].value == "r3"
    assert parse[1][1].rule_name == 'empty_note_or_accent'

test_header_parser()
test_alterations()
test_one_note_neumes()
test_rhythmic_signs()
test_empty_notes()
test_accents()