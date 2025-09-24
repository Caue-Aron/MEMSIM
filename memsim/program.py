import util
from util import MEM_SIZE, NULL, byte
import numpy as np

# Container class
class Program:
    def __init__(self, byte_data:np.array):
        self.bytes = np.array(byte(byte_data), dtype=byte)
    
    def stream_bytes(self):
        return self.bytes.copy()
        