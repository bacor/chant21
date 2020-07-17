import os
CUR_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.path.pardir))
import sys
sys.path.append(ROOT_DIR)

if __name__ == '__main__':
    import doctest
    from chant21 import chant
    doctest.testmod(chant)