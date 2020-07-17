import json
from music21 import converter
from .chant import Chant

class ConverterCHSON(converter.subConverters.SubConverter):
    registerFormats = ('chson', 'CHSON')
    registerInputExtensions = ('chson', 'CHSON')
    
    def parseData(self, strData, number=None):
        chantObj = json.loads(strData)
        chant = Chant()
        chant.fromObject(chantObj)
        self.stream = chant
   
converter.registerSubconverter(ConverterCHSON)