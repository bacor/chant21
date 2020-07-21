import os
CUR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.path.pardir))
import sys
sys.path.append(ROOT_DIR)

if __name__ == '__main__':
    import doctest
    
    from chant21 import converter_cantus_volpiano
    doctest.testmod(converter_cantus_volpiano)

    from chant21 import parser_cantus_volpiano
    doctest.testmod(parser_cantus_volpiano)

    from chant21 import syllabifier
    doctest.testmod(syllabifier)