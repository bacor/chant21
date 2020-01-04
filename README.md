GABC2Volpiano
=============

A Python package for converting 
[GABC](http://gregorio-project.github.io/gabc/index.html) 
to [Volpiano](http://www.fawe.de/volpiano/), two text-based formats for 
notating Gregorian chant.

The package expresses the GABC syntax as a [parsing expression grammar](
https://en.wikipedia.org/wiki/Parsing_expression_grammar)
(inspired by [gabc-converter](https://github.com/saybaar/gabc-converter)).
The grammar can be found in `gabc2volpiano/gabc.peg`. We then use 
[Arpeggio](http://textx.github.io/Arpeggio) to parse GABC files and the 
resulting parse tree is then converted to a Volpiano string (the music) and 
a text string (the lyrics). 

Examples
--------

```python
>>> from gabc2volpiano import VolpianoConverter
>>> converter = VolpianoConverter()
>>> text, volpiano = converter.convert('(c3) He(f)llo(gf) world(ghgf)')
>>> text, volpiano
(' He-llo world', '1---h--jh---jkjh')
```

```python
>>> from gabc2volpiano import VolpianoConverter
>>> converter = VolpianoConverter()
>>> file_contents = (
"""name:Kyrie;
mode:1;
%%
(c4) KY(ixhi)ri(hg)e(hd..) *(,) e(fhGE'D)lé(c')i(d)son.(d.)""")
>>> header, text, volpiano = converter.convert_file_contents(file_contents)
>>> header
{'name': 'Kyrie', 'mode': '1'}
>>> text, volpiano
(' KY-ri-e * e-lé-i-son.', '1---ihj--hg--hd---7---fhged--c--d--d')
```

Tests
-----

The PEG grammar, parser and converter are all extensively tested.
To run all tests:

```bash
$ python -m unittest discover tests/ "test_*.py" 
```

Dependencies
------------

- [Arpeggio 1.9.2](http://textx.github.io/Arpeggio)