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
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Multimedia :: Sound/Audio :: Conversion'
]

setuptools.setup(
    name="chant21",
    version=chant21version,
    python_requires='>=3.7',
    author="Bas Cornelissen",
    license="MIT License",
    description="Plainchant in Python",
    long_description=(
        "`chant21` is a library for plainchant in Python. It contains converters"
        "from GABC and Volpiano to `music21`, preserves the exact textual "
        "structure of the  chant, and allows you to interactively explore "
        "this in Jupyter notebooks. For details, refer to the "
        "[GitHub repository](https://github.com/bacor/chant21) "
        "or the [documentation](https://chant21.readthedocs.io/)."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/bacor/chant21",
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    install_requires=[
        "music21>=5.7.2,<8.0",
        "Arpeggio>=1.9.2",
        "Jinja2>=2.11.1",
        "PyYAML==5.3.1"
    ],

    # Which data files to include, see 
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
    package_data = {
        "chant21": [
            "*/*.peg"
            "*/*.yml",
            "html/*.html",
            "examples/*.gabc",
            "examples/*.csv",
        ]
    }
)
