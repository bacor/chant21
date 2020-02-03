import jinja2
import os.path as path

CUR_DIR = path.dirname(__file__)
TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath=CUR_DIR)
TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)
WIDGET = TEMPLATE_ENV.get_template('widget.html')
FILE = TEMPLATE_ENV.get_template('file.html')

def toWidget(chant, showDisplayOptions=True, showSections=False, 
    showWords=False, showSyllables=False, showNeumes=False):
    """"""
    obj = chant.toObject(includeVolpiano=True)
    html = WIDGET.render(chant=obj, 
                         showDisplayOptions=showDisplayOptions,
                         showSections=showSections, 
                         showWords=showWords,
                         showSyllables=showSyllables, 
                         showNeumes=showNeumes)
    return html

def toFile(chant, filepath=None, showDisplayOptions=True,
    showSections=False, showWords=False, showSyllables=False, 
    showNeumes=False):
    """"""
    obj = chant.toObject(includeVolpiano=True)
    html = FILE.render(chant=obj, 
                         showDisplayOptions=showDisplayOptions, 
                         showSections=showSections, 
                         showWords=showWords,
                         showSyllables=showSyllables, 
                         showNeumes=showNeumes)
    if filepath is None:
        return html
    else:
        with open(filepath, 'w') as handle:
            handle.write(html)
