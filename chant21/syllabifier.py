"""
Latin Syllabifier Wrapper around the CLTK syllabifier, specifically adjusted for
chant.
"""
from .cltk_syllabifier import Syllabifier
from .cltk_syllabifier import LATIN
from copy import deepcopy
import yaml
import os

# Make adjustments to the CLTK settings for Latin, to optimize it for chant
CHANT_LATIN = deepcopy(LATIN)
CHANT_LATIN['diphthongs'] = ["ae", "au", "oe"] # Not: eu, ei
CHANT_LATIN['mute_consonants_and_f'].append('h')
cur_dir = os.path.dirname(__file__)
exceptions_fn = os.path.join(cur_dir, 'syllabifier-exceptions.yml')
with open(exceptions_fn, 'r') as stream:
    exceptions = yaml.safe_load(stream)
    CHANT_LATIN['exceptions'].update(exceptions)

class ChantSyllabifier(Syllabifier):
    def __init__(self):
        super().__init__(CHANT_LATIN)
    
    def syllabify(self, text: str) -> list:
        """Syllabifies a string of Latin. 
        
        CLTK works best with lowercased input, so we first syllabify the 
        lowercased text and then copy the segmentation to the original input 
        string.

        >>> syllabifier = ChantSyllabifier()
        >>> syllabifier.syllabify('Lorem Ipsum DOLOR')
        ['Lo', 'rem', ' Ip', 'sum', ' DO', 'LOR']
        >>> syllabifier.syllabify('euouae')
        ['e', 'u', 'o', 'u', 'a', 'e']
        >>> syllabifier.syllabify('kyrieleison')
        ['ky', 'ri', 'e', 'lei', 'son']

        Parameters
        ----------
        text : str
            The latin text to syllabifiy

        Returns
        -------
        list
            A list of syllables.
        """
        lowercased_syllables = super().syllabify(text.lower())
        syllables = []
        pos = 0
        for lowercased_syllable in lowercased_syllables:
            syllable = text[pos:pos+len(lowercased_syllable)]
            syllables.append(syllable)
            pos += len(lowercased_syllable)
        return syllables
