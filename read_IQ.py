import numpy as np
import scipy as sp

'''
this is to convert the IQ stream of data to ADSB message patter
'''

# Read the file
arr = np.fromfile('test_data.dat',np.uint8)
print 'shape of the array (%d,)' %(arr.shape[0])

iter=0
while (iter < 48):
    i=0
    msg=""
    time=np.base_repr(iter, base=16,padding=(7-len(np.base_repr(iter, base=16))))
    msg=time+" "
    for i in xrange(8):
        msg+=np.base_repr(arr[iter+2*i], base=16)
        msg+=np.base_repr(arr[iter+2*i+1], base=16)
        msg+=' '
    print msg
    iter+=16
