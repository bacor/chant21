import os
EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
kyrie = os.path.join(EXAMPLES_DIR, 'kyrie.gabc')
salveRegina = os.path.join(EXAMPLES_DIR, 'salve_regina.gabc')
utQueantLaxis = os.path.join(EXAMPLES_DIR, 'ut_queant_laxis.gabc')
abOrtuSolis = os.path.join(EXAMPLES_DIR, 'ab_ortu_solis.gabc')
gabcExamples = {
    'kyrie': kyrie,
    'salveRegina': salveRegina,
    'utQueantLaxis': utQueantLaxis,
    'abOrtuSolis': abOrtuSolis
}
