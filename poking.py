import numpy as np

x = np.array([10, 20, 30, 40, 50])
i = 0
for v in x:
    print("%s, %s" % (i, v))
    if v in (10, 30, 40):
        x = np.delete(x, i)
    else:
        i += 1
x
x
x = np.delete(x, 1)
x
