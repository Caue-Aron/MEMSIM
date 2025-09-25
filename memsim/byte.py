import numpy as np

class Byte(np.uint16):    
    def __new__(cls, value:int=0):
        return super().__new__(cls, value)

    def __repr__(self):
        return f"0x{int(self):04X}"
    
NULL = Byte(0)