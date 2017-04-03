import sys
import os
import time


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        #print "bytes = %f" %(file_info.st_size)
        return file_info.st_size


#file=open('data/test_data.dat','rb')
file=open(sys.argv[1],'rb')
print 'File Size: %f Mb' %(file_size(sys.argv[1])/(4.0*16*16384))
list=file.readline()

start=0
c=0

start_time = time.time()
while start<len(list):
    if((start+65536*16)<=len(list)):
        e=(start+65536*16)    # Start and end of the IQ data that has to stored to the bin file
    else:
        e=len(list)
    f=open('test.bin','w')
    f.write(list[start:e])    # This makes sure that only 1Mb of data is writen to the bin file
    f.close()

    # Error show if the file is greater than 1Mb
    if(file_size('test.bin')>(4*16*16384)):
        print '************************Error in size*********************** '
        break

    #print "%d:Start: %d||End: %d||Size: %dMb" %(c,start,e,file_size('test.bin')/(65536.0*16.0))
    
    os.system("python mode_s.py test.bin")
    start+=4*16*16384
    c+=1
    os.remove('test.bin')
    print '################################## %d ###############################' %(c)
print 'Time taken for the program: %d' %(-start_time+time.time())
