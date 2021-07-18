import numpy as np
from collections import OrderedDict
'''
a = np.array([[1,2,3,4,5,6],[2,3,4,5,6,7]])
b = np.where(a>3)
for i in zip(b[0],b[1]):
    print(i)

'''

class Frontier(OrderedDict):
    def enqueue(self, key, value=None):
        # Does nothing if the key is already in the queue
        self.__setitem__(key, value)

    def dequeue(self, get_value=False):
        if get_value:
            return self.popitem(last=False)
        else:
            return self.popitem(last=False)[0]


a = Frontier()
a.enqueue('a',1)

print(a)
for x,y in a.items():
    print(x,y)

a.pop('a')
print(a)