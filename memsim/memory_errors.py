from .byte import Byte, NULL
from .safe_list import SafeList
from typing import Dict, List

class MemSimError(Exception):
    pass

class MSNotEnoughMemory(MemSimError):
    def __init__(self, memory:List[Byte], layout:SafeList[Dict[str, int]], requested:int):
        super().__init__(f"Not enough memory for the requested block: {requested}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.requested_block = requested
