import numpy as np
import struct

def ReadBinFileHeader(filename):
	f = open(filename,"r")
	binary_file = np.fromfile(f,dtype=np.uint32,count=4)
	number_of_events = binary_file[0]
	length_per_waveform = binary_file[1]    
	return number_of_events,length_per_waveform


def bitfield(n):
    tmp = [1 if digit=='1' else 0 for digit in bin(n)[2:]]
    return tmp[::-1]


def ReadBinFile(fName):
    #fName = "test.bin"
    waveInfo = {}
    
    fp = open(fName,"rb")
    
    numEvents = int(np.fromfile(fp,dtype=np.uint32,count=1))
    waveInfo['numEvents'] = numEvents
    numSamples = int(np.fromfile(fp,dtype=np.uint32,count=1))
    waveInfo['numSamples'] = numSamples
    chSelMask = int(np.fromfile(fp,dtype=np.uint32,count=1))
    chMap = np.where(bitfield(chSelMask))[0]
    waveInfo['chMap'] = chMap
    numChannels = len(chMap)
    waveInfo['numChannels'] = numChannels
    byteOrderPattern = hex(int(np.fromfile(fp,dtype=np.uint32,count=1)))
    
    waveArr = np.zeros((numChannels,numEvents,numSamples),dtype=np.int16)
    
    for ievt in range(numEvents):
        for ich in range(numChannels):
            dummy = np.fromfile(fp,dtype=np.uint32,count=2)
            waveTmp = np.fromfile(fp,dtype=np.int16,count=numSamples)
            waveArr[ich,ievt,:] = waveTmp
            dummy = np.fromfile(fp,dtype=np.uint32,count=1)
    fp.close()
    return (waveArr,waveInfo)


def B2T(filename,channel):
	waveform,waveInfo = ReadBinFile(filename)
	if(channel>=len(waveInfo['chMap'])):
		print("Cannot find channel. Check user supplied index")
		return

	s = filename.rstrip(".bin")
	s += ".txt"
	lend = "\n"
	fout = open(s,"w")
	for i in range(waveInfo['numEvents']):
		fout.write("Event "+str(i)+str(lend))
		for j in range(waveInfo['numSamples']):
			s = str(waveform[channel,i,j])+lend
			fout.write(s)
	fout.close()


def ReadBinFilelk_leg(filename,number_of_channels,event):
	f = open(filename, "r")
	binary_file = np.fromfile(f, dtype=np.int16)
	bit1 = binary_file[0]
	bit2 = binary_file[1]
	
	if np.logical_and(bit2==0,bit1>0):
		number_of_events = bit1
	elif np.logical_and(bit2==1,bit1<0):
		number_of_events = 2**17+bit1
	else:
		number_of_events = 2**16+bit1
	print(number_of_events)
	length_per_waveform = binary_file[2]
	print(str(length_per_waveform))
	start_skip = 12
	deadspace_between_channels = 6
	#binary_file = binary_file[6:]
	#binary_file = binary_file.tobytes()
	#binary_file = np.fromstring(binary_file,dtype=np.int16)
	waveform_array = np.zeros(shape=(number_of_channels,length_per_waveform),dtype=np.int16)
	one_event_length = number_of_channels*(length_per_waveform+deadspace_between_channels)
	for j in range(number_of_channels):
		current_index_location = start_skip + event*(one_event_length)+ j*(length_per_waveform+ deadspace_between_channels)		
		waveform_array[j] = binary_file[current_index_location:current_index_location+length_per_waveform]
	return waveform_array    

def B2T_leg(filename,number_of_channels,channel):
	f = open(filename, "r")
	binary_file = np.fromfile(f, dtype=np.int16)
	bit1 = binary_file[0]
	bit2 = binary_file[1]
	
	if np.logical_and(bit2==0,bit1>0):
		number_of_events = bit1
	elif np.logical_and(bit2==1,bit1<0):
		number_of_events = 2**17+bit1
	else:
		number_of_events = 2**16+bit1
	print(number_of_events)
	length_per_waveform = binary_file[2]
	print(str(length_per_waveform))
	start_skip = 12
	deadspace_between_channels = 6
	#binary_file = binary_file[6:]
	#binary_file = binary_file.tobytes()
	#binary_file = np.fromstring(binary_file,dtype=np.int16)
	lend = "\n"
	s = filename.rstrip(".bin")
	s += ".txt"
	fout = open(s,"w")
	waveform_array = np.zeros(shape=(length_per_waveform),dtype=np.int16)
	one_event_length = number_of_channels*(length_per_waveform+deadspace_between_channels)
	for i in range(number_of_events):
		fout.write("Event "+str(i)+str(lend))
		current_index_location = start_skip + i*(one_event_length)+ channel*(length_per_waveform+ deadspace_between_channels)
		waveform_array = binary_file[current_index_location:current_index_location+length_per_waveform]
		for j in range(samples):
			s = str(waveform_array[j])+lend
			fout.write(s)
	fout.close()
	   



