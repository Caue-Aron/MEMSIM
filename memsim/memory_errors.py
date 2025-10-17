from .byte import Byte, NULL
from .safe_list import SafeList
from typing import Dict, List
from .segment import Segment

class MemSimError(Exception):
    pass

class MSNotEnoughMemory(MemSimError):
    def __init__(self, memory:List[Byte], layout:SafeList[Segment], requested:int):
        super().__init__(f"Not enough memory for the requested block: {requested}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.requested_block = requested

class MSNotEnoughDiscMemory(MemSimError):
    def __init__(self, memory:List[Byte], layout:SafeList[Segment], requested:int):
        super().__init__(f"Not enough disc memory for the requested block: {requested}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.requested_block = requested

class MSFaultyAccess(MemSimError):
    def __init__(self, memory:List[Byte], layout:SafeList[Segment], block:Segment):
        super().__init__(f"Faulty access at block: {block}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.block = block

class MSNoAllocationBlockAvailable(MemSimError):
    def __init__(self, memory:List[Byte], layout:SafeList[Segment], block:Segment):
        super().__init__(f"No allocation section available for: {block}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.block = block

class MSIDNotFound(MemSimError):
    def __init__(self, id_search:int, memory:List[Byte], layout:SafeList[Segment]):
        super().__init__(f"No match found for ID {id_search}\nMemory logged")

        self.memory = memory
        self.layout = layout
        self.id = id_search