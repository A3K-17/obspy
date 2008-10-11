# -*- coding: utf-8 -*-

from obspy.seed.blockette import Blockette 
from obspy.seed.fields import Integer, VariableString


class Blockette034(Blockette):
    """Blockette 034: Units Abbreviations Blockette.
    
    This blockette defines the units of measurement in a standard, repeatable 
    way. Mention each unit of measurement only once.
    
    Sample:
    0340044001M/S~Velocity in Meters Per Second~
    """
    
    id = 34
    name = "Units Abbreviations Blockette"
    fields = [
        Integer(3, "Unit lookup code", 3),
        VariableString(4, "Unit name", 1, 20, 'UNP'),
        VariableString(5, "Unit description", 0, 50, 'UNLPS')
    ]
