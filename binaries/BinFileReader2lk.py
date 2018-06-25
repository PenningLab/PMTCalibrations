import numpy as np
import struct

def ReadBinFileHeader(filename):
	f = open(filename,"r")
	binary_file = np.fromfile(f,dtype=np.uint32,count=4)
	number_of_events = binary_file[0]
	length_per_waveform = binary_file[1]    
	return number_of_events,length_per_waveform


def ReadBinFilelk(filename,number_of_channels,event):
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

def ReadBinFile(filename,number_of_channels):
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
	#number_of_events = binary_file[0]
	length_per_waveform = binary_file[2]
	start_skip = 12
	deadspace_between_channels = 6
	waveform_array = np.zeros(shape=(number_of_channels,number_of_events,length_per_waveform),dtype=np.int16)
	one_event_length = number_of_channels*(length_per_waveform+deadspace_between_channels)
	for i in range(number_of_events):
		print("event "+str(i))
		for j in range(number_of_channels):
			current_index_location = start_skip +i*(one_event_length)+ j*(length_per_waveform+ deadspace_between_channels)
			waveform_array[j,i] = binary_file[current_index_location:current_index_location+length_per_waveform]
	return waveform_array,number_of_events

def ReadBinFilelk2(filename,channels,evt):
	Nevts, samples = ReadBinFileHeader(filename)
	f = open(filename,"r")
	ba = bytearray(f.read())
	print(len(ba))
	samples = samples
	waveforms = np.zeros(shape=(channels,samples),dtype=np.int16)
	skip = 24
	deadspace = 6
	for j in range(channels):
		indexlow = skip + 2*evt*channels*(samples+deadspace) + 2*j*(samples+deadspace)
		for k in range(samples):
			indexlowk = indexlow +2*k
			thispoint = ba[indexlow:(indexlow + 2)]
			waveforms[j][k] = int.from_bytes(thispoint, byteorder='big',signed=True)
	return waveforms



def B2T(filename,number_of_channels,channel):
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
	   
