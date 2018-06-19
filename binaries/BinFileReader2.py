import numpy as np

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
    number_of_events = binary_file[0]
    length_per_waveform = binary_file[2]
    start_skip = 12
    deadspace_between_channels = 6
    waveform_array = np.zeros(shape=(number_of_channels,number_of_events,length_per_waveform),dtype=np.float16)
    one_event_length = number_of_channels*(length_per_waveform+deadspace_between_channels)
    for i in range(number_of_events):
        for j in range(number_of_channels):
            current_index_location = start_skip +i*(one_event_length)+ j*(length_per_waveform+ deadspace_between_channels)
            waveform_array[j,i] = binary_file[current_index_location:current_index_location+length_per_waveform]
    return waveform_array,number_of_events
