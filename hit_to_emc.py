import sys
import numpy as np
import h5py
import argparse
sys.path.append('/home/ayyerkar/.local/dragonfly/utils/py_src')
import writeemc
import os

parser = argparse.ArgumentParser(description='Convert hits file to sparse EMC H5 file')
parser.add_argument('-r', '--run', type=int, help='Run number')
parser.add_argument('-p', '--path', type=str, help='Path to hits files',default = '/gpfs/exfel/exp/SQS/201901/p002146/scratch/hits')
parser.add_argument('-o', '--out_folder', help='Path to output folder',default='/gpfs/exfel/exp/SQS/201901/p002146/scratch/emc')
parser.add_argument('-t', '--adu_threshold', help='ADU threshold', type=float, default=200)
args = parser.parse_args()

hitfiles = os.path.join(args.path + "/r%04d_hits.h5" %(args.run))
emcfile = os.path.join(args.out_folder, 'r%04d_emc.h5'%(args.run))
emc = writeemc.EMCWriter(emcfile, 1024*1024)

photon_ADU = args.adu_threshold


with h5py.File(hitfiles,'r') as fptr:
	nframes = fptr['hits'].shape[0]
	for i in range(nframes):
		emc.write_frame(fptr['hits'][i].ravel().astype('i4'))
		#emc.write_frame(np.round(fptr['hits'][i]/photon_ADU).ravel().astype('i4'))
		sys.stderr.write('\r%d/%d'%(i+1, nframes))

emc.finish_write()

os.system('chmod ao+rw %s' % (emcfile))
                                         
