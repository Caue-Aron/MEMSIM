from .util import *
import numpy as np
from numpy.typing import NDArray

# Container class
class Program:
    def __init__(self, byte_data:list):
        self.bytes = np.array(byte(byte_data), dtype=byte)
    
    def stream_bytes(self):
        return self.bytes.copy()
        