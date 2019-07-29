import sys
import numpy as np
import h5py
import argparse
sys.path.append('/home/ayyerkar/.local/dragonfly/utils/py_src')
import detector

Rmax = 1024

det = detector.Detector()
x,y = np.indices((1024,1024))
x -= 512
y -= 512
det.cx = x.astype('f8').ravel()
det.cy = y.astype('f8').ravel()
det.detd = 350
det.ewald_rad = 200
det.calc_from_coords()

det.raw_mask = np.array(h5py.File('../mask.h5','r')['data/data'])
det.raw_mask = 2-2*det.raw_mask
rad = np.sqrt(det.cx**2+det.cy**2).reshape(1024,1024)
det.raw_mask[(det.raw_mask==0) & (rad>Rmax)] = 1

det._write_h5det('../dragonfly_mask.h5')
