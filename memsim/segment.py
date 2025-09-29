HOLE = "H"
PROGRAM = "P"

class Segment:
    def __init__(self, stype:str, index:int, size:int):
        self.type = stype
        self.index = index
        self.size = size

    def __repr__(self):
        return f"{self.type}, {self.index}, {self.size}"
    
    def copy(self):
        return Segment(self.type, self.index, self.size)