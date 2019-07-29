import numpy as np
import pyqtgraph as pg
import h5py
import argparse
import glob
import os
from matplotlib import pyplot as plt

# ---- constants

# ---- functions

def read_data(my_path,run_num,dark,calib):
    path_tot = my_path+'r{:04d}/'.format(run_num)
    if calib:
        flist = [f for f in os.listdir(path_tot) if 'RAW-R{:04d}-PNCCD01-'.format(run_num) in f]
    else:
        flist = [f for f in os.listdir(path_tot) if 'CORR-R{:04d}-PNCCD01-'.format(run_num) in f]
    flist.sort()
    print(flist)
    bin_counts = []
    for file in flist:
        if calib:
            data = np.array(h5py.File(os.path.join(path_tot,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image'])
            data = calibrate_data(data,dark)
        else:
            data = np.array(h5py.File(os.path.join(path_tot,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/pixels_cm'])
        
        bin_values,bin_edges = np.histogram(data,bins=500,range=(-1000,8000))
        bin_counts.append(bin_values)
    bin_centers = np.array([(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(bin_edges)-1)],dtype=int)
    bin_counts = np.sum(np.array(bin_counts),axis=0)

    return bin_centers, bin_counts

def read_dark(my_path,run_num,calib):
    path_tot = my_path + 'r{:04d}/'.format(run_num)
    print(path_tot)
    if calib:
        flist_dark = [f for f in os.listdir(path_tot) if 'RAW-R{:04d}-PNCCD01-'.format(run_num) in f]
        data = [np.array(h5py.File(os.path.join(path_tot,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image']) for file in flist_dark]
    else:
        flist_dark = [f for f in os.listdir(path_tot) if 'CORR-R{:04d}-PNCCD01-'.format(run_num) in f]
        data = [np.array(h5py.File(os.path.join(path_tot,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/pixels_cm']) for file in flist_dark]
    print(flist_dark)
    print(len(data))
    if len(data) > 1:
        data = np.vstack(data)
        data = np.mean(data,axis=0)
    else: 
        data = np.array(data)
    
    return data

    
def calibrate_data(raw,background):
    print('Calibrate data...')
    #offset = np.mean(background,axis=0,keepdims=True)
    data_offset = raw-background
    #data_corr = np.reshape(data_offset,(data_offset.shape[0],data_offset.shape[1],2,data_offset.shape[2]//2)) 
    #med1 = np.median(data_corr[:,:,0,:],axis=2,keepdims=True)
    #med2 = np.median(data_corr[:,:,1,:],axis=2,keepdims=True)
    #data_corr[:,:,0,:] -= med1
    #data_corr[:,:,1,:] -= med2
    #data_corr = data_corr.reshape((data_offset.shape[0],data_offset.shape[1],data_offset.shape[1]))
    #return data_corr
    upper = data_offset[:,:,:data_offset.shape[2]//2]
    lower = data_offset[:,:,data_offset.shape[2]//2:]
    med1 = np.median(upper,axis=2,keepdims=True)
    med2 = np.median(lower,axis=2,keepdims=True)
    data_offset[:,:,:data_offset.shape[2]//2] -= med1
    data_offset[:,:,data_offset.shape[2]//2:] -= med2
    left = data_offset[:,:data_offset.shape[1]//2,:]
    right = data_offset[:,data_offset.shape[1]//2:,:]
    med3 = np.median(left,axis=1,keepdims=True)
    med4 = np.median(right,axis=1,keepdims=True)
    data_offset[:,:data_offset.shape[1],:] -= med3
    data_offset[:,data_offset.shape[1]:,:] -= med4

    #with h5py.File('data_corr_chunk_{}'.format(chunk),'w') as f:
    #    f.create_dataset('data',data=data_offset)
    print('Done.')
    return data_offset

# ---- main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='calculate number of hits')
    parser.add_argument('-r','--run',type=int,help='Run number')
    parser.add_argument('-p','--path',type=str,default='/gpfs/exfel/exp/SQS/201901/p002146/raw/',help='Path to data')
    parser.add_argument('-c','--calib',type=int,help='Calibrate data?',default=1)
    parser.add_argument('-d', '--dark', type=int, help='dark run number')

    args = parser.parse_args()

    if args.calib == 1:
        calibrate = True
        path = '/gpfs/exfel/exp/SQS/201901/p002146/raw/'
    else:
        calibrate = False
        path = '/gpfs/exfel/exp/SQS/201901/p002146/proc/'
      
    dark_data = read_dark(path,args.dark,calibrate) 
    bin_x, bin_y = read_data(args.path,args.run,dark_data,calibrate)
    plt.figure()
    plt.plot(bin_x,bin_y)
    plt.yscale('log')
    plt.xlabel('ADUs')
    plt.ylabel('Frequency')
    plt.show()  
