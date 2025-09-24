import numpy as np

byte = np.uint16
NULL = byte(0x00)

def byte_str(data:byte):
    return f"0x{data:04X}"