from .byte import Byte

class SafeList(list):
    def __getitem__(self, index):
        if not isinstance(index, int):
            # allow slicing as usual
            return super().__getitem__(index)
        
        if index < 0:
            index = 0

        elif index >= len(self):
            index = len(self) - 1

        return super().__getitem__(index)
    
    def __repr__(self):
        width = self._value.itemsize * 2 
        return "{" + ", ".join(f"0x{i:{width}X}: {v!r}" for i, v in enumerate(self)) + "}"