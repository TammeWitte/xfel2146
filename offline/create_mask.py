import numpy as np
import h5py
import pyqtgraph as pg
import argparse
import os
import matplotlib.pyplot as plt
import pyqtgraph as pg

# ---- constants
hot_pix_thr = 30000


# ---- functions
def parse_flist(my_path,calib):
    names = [f for f in os.listdir(my_path) if 'PNCCD01' in f]
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

def calibrate_dark(background):
    print('Calibrate data...')
    #offset = np.mean(background,axis=0,keepdims=True)
    data_offset = background
    #data_corr = np.reshape(data_offset,(data_offset.shape[0],data_offset.shape[1],2,data_offset.shape[2]//2)) 
    #med1 = np.median(data_corr[:,:,0,:],axis=2,keepdims=True)
    #med2 = np.median(data_corr[:,:,1,:],axis=2,keepdims=True)
    #data_corr[:,:,0,:] -= med1
    #data_corr[:,:,1,:] -= med2
    #data_corr = data_corr.reshape((data_offset.shape[0],data_offset.shape[1],data_offset.shape[1]))
    #return data_corr
    upper = data_offset[:,:data_offset.shape[1]//2]
    lower = data_offset[:,data_offset.shape[1]//2:]
    med1 = np.median(upper,axis=1,keepdims=True)
    med2 = np.median(lower,axis=1,keepdims=True)
    data_offset[:,:data_offset.shape[1]//2] -= med1
    data_offset[:,data_offset.shape[1]//2:] -= med2
    left = data_offset[:data_offset.shape[0]//2,:]
    right = data_offset[data_offset.shape[0]//2:,:]
    med3 = np.median(left,axis=0,keepdims=True)
    med4 = np.median(right,axis=0,keepdims=True)
    data_offset[:data_offset.shape[0],:] -= med3
    data_offset[data_offset.shape[0]:,:] -= med4

    #with h5py.File('data_corr_chunk_{}'.format(chunk),'w') as f:
    #    f.create_dataset('data',data=data_offset)
    print('Done.')
    return data_offset


def find_hit(my_path,run):
    f = h5py.File(os.path.join(my_path,'r{:04d}_hits.h5'.format(run)),'r')
    hits = f['hits']
    strongest_hit = np.argmax([np.sum(hit) for hit in hits])
    return hits[strongest_hit]
    #with h5py.File('powder.h5','w') as g:
    #    g.create_dataset('powder',data=powder)
        
    return powder

def apply_geom(powder): 
    geom = np.zeros((powder.shape[0]+args.gap,powder.shape[1]+args.shift))
    #geom.fill(np.nan)
    geom[:powder.shape[0]//2,args.shift:1024+args.shift] = powder[:powder.shape[0]//2,:]
    geom[powder.shape[0]//2+args.gap:,:powder.shape[1]] = powder[powder.shape[0]//2:,:]       
    return geom

def calc_mask(background,hit):
    mask_pre = np.ones_like(hit)
    mask_pre *= (background < hot_pix_thr)*(hit < hot_pix_thr)
    return mask_pre

 
# ---- main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='calculate number of hits')
    parser.add_argument('-r','--run',type=int,help='Run number')
    parser.add_argument('-p','--path',type=str,default='/gpfs/exfel/exp/SQS/201901/p002146/')
    parser.add_argument('-g','--gap',type=int,default=49,help='gap')
    parser.add_argument('-s','--shift',type=int,default=12,help='Upper panel shift')
    parser.add_argument('-d','--dark',type=int,help='Dark run number')
    parser.add_argument('-c','--calib',type=int,help='Take raw data if calib==1, else proc',default=0)
    args =  parser.parse_args()
    if args.calib == 1:
        calibrate = True
        path = '/gpfs/exfel/exp/SQS/201901/p002146/raw/'
    else:
        calibrate = False
        path = '/gpfs/exfel/exp/SQS/201901/p002146/proc/'

    dark_path = path+'r{:04d}'.format(args.dark)
    hit_path = args.path+'scratch/hits/'

    #pwd = read_powder(pwd_path,args.run)
    flist = parse_flist(dark_path,args.calib)
    dark = read_data(dark_path,flist,args.calib) 
    dark = np.mean(dark,axis=0)
    if calibrate:
        dark = calibrate_dark(dark)
    #pg.show(dark[::10,::10])
    
    best_hit = find_hit(hit_path,args.run)
    
    fig, axes = plt.subplots(2,2)
    axes[0,0].imshow(dark)
    axes[1,0].hist(dark.ravel(),bins=500)
    axes[1,0].set_yscale('log')
    axes[0,1].imshow(best_hit)
    axes[1,1].hist(best_hit.ravel(),bins=500)
    axes[1,1].set_yscale('log') 
    
    mask = calc_mask(dark,best_hit)
    
    plt.figure()
    plt.imshow(mask)
    plt.colorbar()
    plt.show()
    
    with h5py.File('mask_preliminary.h5','w') as f:
        f.create_dataset('mask',data=mask)

    
    
