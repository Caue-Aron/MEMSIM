import numpy as np

byte = np.uint16

def byte_str(data:byte):
    return f"0x{data:04X}"

MEM_SIZE = np.iinfo(byte).max + 1
NULL = byte(0x00)