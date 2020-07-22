# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         html/__init__.py
# Purpose:      exporting Chant objects to HTML
#
# Authors:      Bas Cornelissen
#
# Copyright:    Copyright © 2020-present Bas Cornelissen
# License:      see LICENSE
# ------------------------------------------------------------------------------
"""
Chant objects (:class:`chant21.Chant`) objects can be exported to HTML. The music 
will be shown in the `Volpiano typeface <http://www.fawe.de/volpiano/>`_, with 
the lyrics aligned to it; the idea is borrowed from the `Cantus website 
<http://cantus.uwaterloo.ca/home>`_. HTML exports are used when showing chants in
Jupyter notebooks, but it can also be used to generate standalone HTML files for 
chants. The module uses `Jinja <https://palletsprojects.com/p/jinja/>`_ to 
generate HTML from templates.

You can also export chant objects using their method :meth:`chant21.Chant.toHTML`:

>>> html1 = myChant.toHTML()
>>> html2 = toWidget(myChant)
>>> html1 == html2
True 
>>> myChant.toHTML(filepath='mychant.html')
>>> toFile(myChant, filepath='mychant.html')

Or in a Jupyter notebook:

>>> chant.show('html')

"""
import jinja2
import os.path as path
from .. import __version__

# Paths of the Jinja templates
CUR_DIR = path.dirname(__file__)
TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath=CUR_DIR)
TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)
WIDGET = TEMPLATE_ENV.get_template('widget.html')
FILE = TEMPLATE_ENV.get_template('file.html')

def toWidget(chant, showOptions=False, showSections=False, 
    showWords=False, showSyllables=False, showNeumes=False,
    showMetadata=False, showMisalignments=True):
    """Export a chant to an HTML widget: a snippet displayed in Jupyter notebooks.
    
    The structure of the chant can be highlighted visually using several flags:
    ``showSections``, ``showWords``, ``showSyllables`` and ``showNeumes``. When
    ``showOptions`` is on, several checkboxes are shown that allow you
    to highlight these interactively.
    
    Args:
        chant (chant21.Chant): A chant object
        showOptions (bool, optional): If True, several checkboxes are 
            shown that allow you to highlight the structure of the chant
            interactively. Defaults to True.
        showSections (bool, optional): Highlight sections? Defaults to False.
        showWords (bool, optional): Highlight words? Defaults to False.
        showSyllables (bool, optional): Highlight syllables? Defaults to False.
        showNeumes (bool, optional): Highlight neumes?. Defaults to False.
        showMetadata (bool, optional): Show a table with all metadata fields?
            Defaults to False.
        showMisalignments (bool, optional): Highlight misaligned text and music?
    
    Returns:
        str: a HTML string
    """
    obj = chant.toObject(includeVolpiano=True)
    html = WIDGET.render(chant=obj,
                         showOptions=showOptions,
                         showSections=showSections, 
                         showWords=showWords,
                         showSyllables=showSyllables, 
                         showNeumes=showNeumes,
                         showMetadata=showMetadata,
                         showMisalignments=showMisalignments)
    return html

def toFile(chant, filepath=None, showOptions=True, showSections=False, 
    showWords=False, showSyllables=False, showNeumes=False,
    showMetadata=False, showMisalignments=True):
    """Export a Chant to an HTML file.
    
    Args:
        chant (chant21.Chant): A chant object
        filepath (string, optional): If a filepath is passed, the html
            is written to that file, otherwise the HTML is returned. 
            Defaults to None.
        **kwargs: you can highlight sections, words, syllables and 
            neumes by passing optional arguments; see :func:`toWidget`.
    
    Returns:
        str: The HTML string is returned if no ``filepath`` is specified.
    """
    obj = chant.toObject(includeVolpiano=True)
    html = FILE.render(chant=obj, 
                       showOptions=showOptions, 
                       showSections=showSections, 
                       showWords=showWords,
                       showSyllables=showSyllables, 
                       showNeumes=showNeumes,
                       showMetadata=showMetadata,
                       showMisalignments=showMisalignments)
    if filepath is None:
        return html
    else:
        with open(filepath, 'w') as handle:
            handle.write(html)
