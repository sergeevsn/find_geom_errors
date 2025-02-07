'''
Finds geometry assignment errors in SEG-Y shot gathers.
Based on simple assumption that the maximum trace energy is on 
the receiver closest to the source. At the same time, there must be 
the smallest offset. If not, we have geometry error. 

At least FFID and OFFSET must be present in trace headers.

SEG-Y File name must be provided in command line
Results text file is set below in parameters
'''
import segyio
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

# program parameters 
RESULT_FILE = "geom_errors.txt"   
PRINT_OUT_HEADERS = {
    'FFID': 9,
    'SourceStation': 233,
}
FIELD_WIDTH = 15    # width of column in result file
PIC_PATH = '.'

try:
    filename = sys.argv[1]
except:
    print('Input filename must be provided!')
    sys.exit(-1)

if not os.path.exists(filename):
    print('Cannot find input filename!')
    sys.exit(-1)

def process_seismogram(seism, offsets):
    rms_amps = np.array([np.sqrt(np.mean(trace**2)) for trace in seism])
    shot_trace_index = np.argmax(rms_amps)
    offsets = np.abs(np.array(offsets))
    min_offset_index = np.argmin(offsets)
    
    return shot_trace_index, min_offset_index

def plot(ffid, seism, shot_trind, minofs_trind):    
    plt.figure(figsize=(10,4))
    vmin, vmax = np.quantile(np.array(seism), [0.02, 0.98])
    plt.imshow(np.array(seism).T, aspect='auto', cmap='gray', vmin=vmin, vmax=vmax)    
    plt.plot(np.ones(seism.shape[1]) * shot_trind , np.arange(seism.shape[1]), label='Near-shot trace')
    plt.plot(np.ones(seism.shape[1]) * minofs_trind , np.arange(seism.shape[1]), label='Minimum offset')
    plt.title(f'FFID {ffid}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PIC_PATH, f'{str(ffid)}.png'))
    plt.close()

rf =  open('geom_errors.txt', 'w')
with segyio.open(filename, strict=False) as f:
    old_ffid = f.header[0][9]    
    
    seismogram = [f.trace[0]]
    offsets = [f.header[0][37]]
    for key in PRINT_OUT_HEADERS.keys():
        rf.write(key.rjust(FIELD_WIDTH))
    rf.write('GeomError'.rjust(FIELD_WIDTH))
    rf.write('\n')
    for i in tqdm(range(1,f.tracecount)):
        ffid = f.header[i][segyio.TraceField.FieldRecord]
        offset = f.header[i][segyio.TraceField.offset]
        trace = f.trace[i]
        source = f.header[i][233]
        
        if (ffid != old_ffid) or (i == f.tracecount - 1):   
            shot_trind, min_ofsind = process_seismogram(seismogram, offsets)
            geom_error = abs(shot_trind - min_ofsind)
            if abs(shot_trind - min_ofsind) > 1:
                printout_headers = [f.header[i-1][byte] for byte in PRINT_OUT_HEADERS.values()]
                for val in printout_headers:
                    rf.write(str(val).rjust(FIELD_WIDTH))
                rf.write(str(geom_error).rjust(FIELD_WIDTH))
                rf.write(f'\n')
                plot(ffid, np.array(seismogram), shot_trind, min_ofsind)
            seismogram = []  
            offsets = []     
        seismogram.append(trace) 
        offsets.append(offset)   
        old_ffid = ffid
        old_source = source
rf.close()