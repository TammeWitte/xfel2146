import numpy as np
import pyqtgraph as pg
import h5py
import argparse
import glob
import os
from matplotlib import pyplot as plt
#plt.ion()



# ---- constants 

chunk_size = 6
limit = 500

# ---- functions
def parse_flist(my_path,run,calib):
    if  calib:
        names = [f for f in os.listdir(my_path) if 'RAW-R{:04d}-PNCCD01-'.format(run) in f]
    else:
        names = [f for f in os.listdir(my_path) if 'CORR-R{:04d}-PNCCD01-'.format(run) in f]
    names.sort()   
    print(names)
    return names

def read_data(my_path,names,calib):
    if calib:
        data_list = [np.array(h5py.File(os.path.join(my_path,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image']) for file in names]
    else:
        data_list = [np.array(h5py.File(os.path.join(my_path,file),'r')['INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/pixels_cm']) for file in names]
    if len(data_list) > 1: 
        data_tot = np.vstack(data_list)
    else:
        data_tot = np.array(data_list)
    print(data_tot.shape)
    return data_tot

def calibrate_data(raw,background,chunk):
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

def find_hits(my_data,t1,path,run):
    print('Find hits...') 
    data_lit = np.zeros_like(my_data)
    data_lit[my_data>t1] = 1
    litpixels = [np.sum(row.ravel()) for row in data_lit]       

    med = np.median(litpixels)
    std = np.std(litpixels)
    hit_threshold = med + 2*std
    hit_list = [i for i,x in enumerate(litpixels) if x>hit_threshold]
    hits = my_data[hit_list]
    return litpixels,hit_list,hit_threshold,hits
    
def write_hits(path,run,hits,litpixels,hit_list,hit_threshold,pwd):
    out_fname = os.path.join(path,'r{:04d}_hits.h5'.format(run))
    with h5py.File(out_fname,'w') as f:
        f.create_dataset('hits',data=np.array(hits))
        f.create_dataset('hit_indices',data=hit_list)
        f.create_dataset('lit_thr',data=hit_threshold)
        f.create_dataset('litpixels',data=litpixels)
        f.create_dataset('powder_sum',data=np.sum(np.array(pwd),axis=0))

# ---- main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='calculate number of hits')
    parser.add_argument('-r','--run',type=int,help='Run number')
    #parser.add_argument('-p','--path',type=str,default='/gpfs/exfel/exp/SQS/201901/p002146/proc/',help='Path to data')
    parser.add_argument('-t','--adu_threshold',type=int,help='ADU threshold',default=200)
    parser.add_argument('-o', '--out_folder', help='Path of output folder (default=/gpfs/exfel/u/scratch/SQS/201901/p002146/hits/)', default='/gpfs/exfel/u/scratch/SQS/201901/p002146/hits/')
    parser.add_argument('-c', '--calib', type=int, help='manual calibration? 1 if True', default=1)
    parser.add_argument('-d', '--dark', type=int, help='dark run number')
    parser.add_argument('-m', '--num_files',type=int,help='set number of files to be read in',default=-1)
    args = parser.parse_args()
    
    if args.calib == 1:
        data_path = '/gpfs/exfel/exp/SQS/201901/p002146/raw/'
        calibrate = True
        
    else:
        data_path = '/gpfs/exfel/exp/SQS/201901/p002146/proc/'
        calibrate = False
    
    path_dark = data_path+'r{:04d}/'.format(args.dark)
    flist_dark = parse_flist(path_dark,args.dark,calibrate)
    dark = read_data(path_dark,flist_dark,calibrate)
    dark = np.mean(dark,axis=0)
    #dark = np.reshape(dark,(dark.shape[0],dark.shape[1]//2,2))
    #dark[:,:,0] -= np.median(dark[:,:,0],axis=1,keepdims=True)
    #dark[:,:,1] -= np.median(dark[:,:,1],axis=1,keepdims=True)
    #dark = dark.reshape((dark.shape[0],dark.shape[0]))
    
    hit_data = []
    lp_list = []
    hit_indices_list = []
    threshold_list = []
    powder_list = []
    path_tot = data_path+'r{:04d}/'.format(args.run)
    flist = parse_flist(path_tot,args.run,calibrate)
    flist = flist[:args.num_files]
    print('Number of files: ', len(flist), ' --> do {} chunks'.format(np.ceil(len(flist)/chunk_size)))
    for i in range(int(np.ceil(len(flist)/chunk_size))):
        print(i%chunk_size)
        my_range = range(i*chunk_size,(i+1)*chunk_size) if ((i+1)*chunk_size)<len(flist) else range(i*chunk_size,len(flist))
        print(my_range)
        flist_red = flist[my_range[0]:my_range[-1]+1] 
        print(flist_red)
        data = read_data(path_tot,flist_red,calibrate)
        if data.shape[0] != 0: 
            if calibrate:
                data = calibrate_data(data,dark,i)
            
            lp, hit_indices, hit_thr, hit_data_i = find_hits(data,args.adu_threshold,args.out_folder,args.run)
            hit_data.extend(hit_data_i)
            powder_list.extend(data[hit_indices])
            lp_list.extend(lp)
            hit_indices_list.extend(list(np.array(hit_indices)+(i*chunk_size*limit)))
            threshold_list.append(hit_thr)
        
    print(len(hit_indices_list))
    print(len(powder_list))
    write_hits(args.out_folder,args.run,hit_data,lp_list,hit_indices_list,threshold_list,powder_list)

    
