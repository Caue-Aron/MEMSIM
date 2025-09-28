from .byte import Byte, NULL
from numpy.typing import NDArray
from typing import List

# Container class
class Program:
    def __init__(self, byte_data:list|List[Byte]):
        self.bytes = [i if isinstance(i, Byte) else Byte(i) for i in byte_data]
    
    def stream_bytes(self):
        return self.bytes.copy()
        