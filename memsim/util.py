from numpy import uint16

byte = uint16
NULL = byte(0x00)

def byte_str(data:byte):
    return f"0x{data:04X}"