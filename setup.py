import setuptools
import os 

# Copied from music21: do not import chant21 directly.
# Instead, read the _version.py file and exec its contents.
path = os.path.join(os.path.dirname(__file__), 'chant21', '_version.py')
with open(path, 'r') as f:
    lines = f.read()
    exec(lines)
chant21version = __version__

classifiers = [
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Multimedia :: Sound/Audio :: Conversion',
    'Topic :: Artistic Software',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chant21",
    version=chant21version,
    python_requires='>=3.7',
    author="Bas Cornelissen",
    author_email="mail@bascornelissen.nl",
    description="A toolkit for Gregorian chant in music21",
    long_description=long_description,
    url="https://github.com/bacor/chant21",
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    install_requires=['music21', 'arpeggio', 'jinja2'],

    # Important: ensure HTML templates in chant21/html are included
    include_package_data=True,
)