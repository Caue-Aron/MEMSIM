from .byte import Byte, NULL
from typing import List
from .memory import Memory, HOLE, PROGRAM, Segment
from .program import Program
from .memory_errors import MSNotEnoughMemory

class RAM(Memory):
    def __init__(self, memory_size:Byte.dtype = Byte.MAX+1):
        super().__init__(memory_size)