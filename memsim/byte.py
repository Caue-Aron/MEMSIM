import numpy as np

class Byte:
    dtype = np.uint16

    MIN = np.iinfo(dtype).min
    MAX = np.iinfo(dtype).max

    def __init__(self, value: int = 0):
        self._value = self.dtype(self._clamp(value))

    @classmethod
    def _clamp(cls, value: int) -> int:
        if value < cls.MIN:
            return cls.MIN
        elif value > cls.MAX:
            return cls.MAX
        return value

    @property
    def value(self) -> int:
        return int(self._value)

    @value.setter
    def value(self, new_value: int):
        self._value = self.dtype(self._clamp(new_value))

    def __str__(self):
        width = self._value.itemsize * 2  # number of hex digits
        return f"0x{self.value:0{width}X}"

    def __repr__(self):
        return str(self)
    
    def __int__(self):
        return int(self._value)
    
    def __eq__(self, value):
        if isinstance(value, int):
            return self._value == value
        
        elif isinstance(value, Byte):
            return self._value == value._value


NULL = Byte(0)