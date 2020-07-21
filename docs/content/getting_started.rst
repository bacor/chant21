Getting started
===============

Let's convert a simple Volpiano chant, and show it as html. Note that this only
works if you have the Volpiano typeface installed.

.. jupyter-execute::

    from music21 import converter
    import chant21
    ch = converter.parse('cantus: 1---f-g--h---g--f--h---3/Abra cadabra')
    ch.show('html')

We have included the lyrics after the slash: chant21 can automatically 
align Latin text to the music.

When chant21 converts a chant, the result is a :class:`chant21.chant.Chant` 
object.  This is a music21 object (a :class:`music21.part.Part`) tweaked to 
better represent chants by retaining the exact division in sections, words, 
syllables and neumes using other custom music21 elements. You can inspect the 
structure using ``ch.show('text')``:

.. jupyter-execute::

    ch.show('text')

Chants imported from the gabc format are represented in the same way:

.. jupyter-execute::

    ch2 = converter.parse('gabc: (c2) a(f)b(g) (::)')
    ch2.show('html')
    ch2.show('text')

You can of course also convert complete files. A handful of GABC and Cantus
examples are included in chant21. Here is one:

.. jupyter-execute::

    from chant21.examples import kyrie as kyrieFilename
    kyrie = converter.parse(kyrieFilename)
    kyrie.show('html')
