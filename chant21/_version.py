"""
Copied from music21._version.py
"""

__version_info__ = (0, 4, 6)

v = '.'.join(str(x) for x in __version_info__[0:3])
if len(__version_info__) > 3 and __version_info__[3]:
    v += __version_info__[3]
if len(__version_info__) > 4:
    v += '.' + '.'.join(__version_info__[4:])

__version__ = v

del v

