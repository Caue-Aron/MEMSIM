from .byte import Byte, NULL
import numpy as np
from numpy.typing import NDArray

# Container class
class Program:
    def __init__(self, byte_data:list):
        self.bytes = Byte(byte_data)
    
    def stream_bytes(self):
        return self.bytes.copy()
        