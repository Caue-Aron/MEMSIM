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