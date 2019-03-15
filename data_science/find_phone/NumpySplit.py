import sys
import numpy as np

'''
a = np.arange(16).reshape(4, 4)

print 'First array:'
print a

print 'Split the array in 2 equal-sized subarrays:'
b = np.split(a, 2)
print 'first', b[0]
print 'second', b[1]

print 'Split sub-arrays in half'
b0 = np.split(b[0], 2, axis=1)
print 'first in half 1', b0[0]
print 'first in half 2', b0[1]
'''

class ArraySplitter(Exception):

    def quarter_array(self, arr):
        by_y = np.split(arr, 2)
        top_y = np.split(by_y[0], 2, axis=1)
        bot_y = np.split(by_y[1], 2, axis=1)
        return top_y[0], top_y[1], bot_y[0], bot_y[1]

if __name__ == '__main__':

    splitter = ArraySplitter()
    arr = np.arange(24).reshape(4, 6)
    print('Initial array=\n{0}'.format(arr))
    res = splitter.quarter_array(arr)
    print('left-top=\n{0}\nright-top=\n{1}\nleft-bottom=\n{2}\nright-bottom=\n{3}'.format(res[0], res[1], res[2], res[3]))


sys.exit(0)

print 'Split the array at positions indicated in 1-D array:'
b = np.split(a, [4, 7])
print b

c = np.arange(24).reshape((4, 6))
print(c)

#d = np.reshape(c, 3)
#print(c)