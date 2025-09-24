from .util import *
import numpy as np
from .safe_list import SafeList
from typing import Dict
from numpy.typing import NDArray

class MemSimError(Exception):
    pass

class MSNotEnoughMemory(MemSimError):
    def __init__(self, memory:NDArray[byte], layout:SafeList[Dict[str, int]], requested:int):
        super().__init__(f"Not enough memory for the requested block: {requested}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.requested_block = requested
