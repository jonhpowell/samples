import sys
import numpy as np

a = np.array([1, 2, 3000, 3001])
print np.std(a)
sys.exit(0)

d = {1:'a', 2:'b', 3:'c'}
print len(d)
sys.exit(0)

ia = np.arange(20).reshape(5, 4)
print('shape={0}, ndim={1}'.format(ia.shape, ia.ndim))
#print ia
for row in range(ia.shape[0]):
#    print('row={0}'.format(ia[row]))
    indices = np.where(ia[row] < 5)
    if len(indices[0]) > 0:
        print('Row {0}: {1}'.format(row, indices[0]))

sys.exit(0)

iar = np.arange(60).reshape(5, 4, 3)
for row in range(iar.shape[0]):
    for col in range(iar.shape[1]):
        mean = iar[row][col].mean()
        if mean < 25:
            print("MEAN RBG @ (row,col) = {2}".format(row, col, mean))

for (row, col), value in np.nditer(iar):
    val = value
    mean = value.mean()
    if mean < 25:
        print("MEAN RBG @ (row,col) = {2}".format(row, col, mean))


print iar
