'''
Author     : C.A. Valliappan
Date       : 24th March 2017
Description: Made few minor changes to the actual mode_s.py
             This code can read IQ data of any size.
             It convert it the IQ data into many 1Mb files.
             These 1Mb files are given as input to readFromFile()
             Outputs will be displayed for every 1Mb file
Addition   : file_size(filename)        ||  [line 182]

'''



from ctypes import *
#from rtlsdr import *
from time import gmtime
from libmodes import *
from pprint import pprint
import sys
import numpy as np
import os
#from bitstring import *
#except ImportError: from .libmodes import libModeS, modesMessage

class ModeSDetectorMessage():
	"""
	Class member variables
	"""
	msg 	= None
	msgpos	= None
	msgbits = None
	msgtype = None
	crcok 	= None
	crc 	= None
	correctedbits 	= None
	corrected 		= None
	addr 			= None
	phase_corrected = None
	timestampMsg	= None
	remote 			= None
	signalLevel 	= None
	capability 		= None
	iid 	= None
	metype 	= None
	mesub 	= None
	heading = None
	raw_latitude 	= None
	raw_longitude 	= None
	fLat 	= None
	fLon 	= None
	flight 	= None
	ew_velocity = None
	ns_velocity = None
	vert_rate 	= None
	velocity 	= None
	fs 			= None
	modeA 		= None
	altitude 	= None
	unit 	= None
	bFlags 	= None

	"""
	Initializes the object with a mode_s message struct
	TODO: support for bflags
	"""
	def __init__(self, modesMessage):
		if sys.version_info[0] >= 3:
			self.msg 	= "".join("{:02x}".format(c) for c in modesMessage.msg)
		else:
			self.msg 	= "".join("{:02x}".format(ord(c)) for c in modesMessage.msg)

		# this msg needs to be sanitized...
		if modesMessage.msgbits == 56:
			self.msg 	= self.msg[:14]
		self.msgpos		= modesMessage.msgpos
		self.msgbits 	= modesMessage.msgbits
		self.msgtype 	= modesMessage.msgtype
		self.crcok 		= False if modesMessage == 0 else True
		self.crc 		= "{:06x}".format(modesMessage.crc)
		self.correctedbits = modesMessage.correctedbits
		self.corrected 	= modesMessage.corrected
		self.addr 		= "{:06x}".format(modesMessage.addr)
		self.phase_corrected = False if modesMessage.phase_corrected == 0 else True
		# note: this timestamp is left out at the moment
		self.timestampMsg 	= gmtime()
		self.remote 		= modesMessage.remote
		self.signalLevel	= ord(modesMessage.signalLevel)
		self.capability		= modesMessage.ca
		self.iid			= modesMessage.iid
		self.metype			= modesMessage.metype
		self.mesub			= modesMessage.mesub
		self.heading		= modesMessage.heading
		self.raw_latitude	= modesMessage.raw_latitude
		self.raw_longitude	= modesMessage.raw_longitude
		self.fLat			= modesMessage.fLat
		self.fLon			= modesMessage.fLon
		self.flight			= modesMessage.flight
		self.ew_velocity	= modesMessage.ew_velocity
		self.ns_velocity	= modesMessage.ns_velocity
		self.vert_rate		= modesMessage.vert_rate
		self.velocity 		= modesMessage.velocity
		self.fs 			= modesMessage.fs
		self.modeA 			= modesMessage.modeA
		self.altitude 	= modesMessage.altitude
		self.unit 		= 'feet' if modesMessage.unit == 0 else 'meter'
		self.bFlags		= modesMessage.bFlags



class ModeSDetector(object):

	ADSB_FREQ = 1090000000
	ADSB_RATE = 2000000
	ADSB_BUF_SIZE = 4*16*16384 # 1MB

	messages = []

	def __init__(self, device_index=0):
		self.device_index = device_index
		libModeS.modesInit()
		libModeS.setPhaseEnhance()
		libModeS.setAggressiveFixCRC()


	def readFromFile(self, filename,buff_size):
        # Added ADSB_BUF_SIZE_2  variable to accomodate the size of the file
        # ADSB_BUF_SIZE_2=buff_size
		with open(filename,'rb') as f:
			while True:
				data = f.read(buff_size)
				if not data:
					break
				else:
					buff = create_string_buffer(data)
					mm = libModeS.processData(buff)
					self.readDataToBuffer(mm)


	def initRTLSDR(self):
		self.rtlsdr = RtlSdr(device_index=self.device_index)
		self.rtlsdr.set_center_freq(self.ADSB_FREQ)
		self.rtlsdr.set_sample_rate(self.ADSB_RATE)
		self.rtlsdr.set_gain(100)
		self.rtlsdr.init = True


	def readFromRTLSDR(self,times):
		if not self.rtlsdr.init:
			self.initRTLSDR()
		if sys.version_info[0] >= 3:
			for i in range(0,times):
			    data = self.rtlsdr.read_bytes(self.ADSB_BUF_SIZE)
			    self.processFromRTLSDR(data)
		else:
			for i in xrange(0,times):
			    data = self.rtlsdr.read_bytes(self.ADSB_BUF_SIZE)
			    self.processFromRTLSDR(data)

	def processFromRTLSDR(self,data,rtlsdr=None):
		mm = libModeS.processData(cast(data,c_char_p))
		self.readDataToBuffer(mm)

	def readFromRTLSDRAsync(self):
		self.rtlsdr.read_bytes_async(self.processFromRTLSDR,num_bytes=self.ADSB_BUF_SIZE)

	def stopReadFromRTLSDRAsync(self):
		self.rtlsdr.cancel_read_async()

	def readDataToBuffer(self,mm):
		while mm:
			message = ModeSDetectorMessage(mm.contents)
			self.messages.append(message)
			mm = mm.contents.next

	def printMessages(self):
		for message in self.messages:
			pprint(vars(message))



def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        #print "bytes = %f" %(file_info.st_size)
        return file_info.st_size


file=open('data/test_data.dat','rb')
list=file.readline()
print len(list)
start=0
c=0

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

    print "%d:Start: %d||End: %d||Size: %fMb" %(c,start,e,file_size('test.bin')/(65536.0*16.0))
    
    modes = ModeSDetector()
    modes.readFromFile("test.bin",file_size("test.bin"))
    modes.printMessages()
    del(modes)
    
    start+=4*16*16384
    c+=1
    os.remove('test.bin')
