class History:
    """
    History class implements a list with maximum length given on object creation. Whenever the maximum length is
    exceeded, the oldest element in the list is thrown out.
    """

    def __init__(self, length):
        self.length = length
        self.list = []

    def __iter__(self):
        return self.list.__iter__()

    def __len__(self):
        return len(self.list)

    def get(self, i):
        if 0 <= i < len(self.list):
            return self.list[i]

    def append(self, o):
        self.list.append(o)
        if len(self.list) > self.length:
            del self.list[0]
