import setuptools

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
    version="0.1.0",
    python_requires='>=3.6',
    author="Bas Cornelissen",
    author_email="mail@bascornelissen.nl",
    description="A toolkit for Gregorian chant in music21",
    long_description=long_description,
    url="https://github.com/bacor/chant21",
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    install_requires=['music21', 'arpeggio', 'jinja2']
)