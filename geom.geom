; KA: Updated geometry to match det_2160_lowq7.h5
; KA: Keeping only 8 low-Q panels
; KA: Manually optimized with hdfsee to match run 48 AgBe rings
; KA: Manually optimized with hdfsee to match AgBe rings (24.05.2019)
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Optimized panel offsets can be found at the end of the file
; OY: I think this is a very well optimized geometry!
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Camera length from LiTiO calibration
; Manually optimized with hdfsee
; Now all distances between panels is 5.8mm (29 pixels)
; OY: ACHTUNG! Orientation of the 2 halves of the detector might be wrong!
; A bit changed by OY: now 128 panels, rigid groups, bad lines to mask double pixels.
; Fixed errors noticed by Oleksandr
; Beginning of an AGIPD geometry construction by Helen Ginn on Thursday before beam time.
; Global panel positions not guesses
; Local positioning largely - but not entirely - guesses
; fast and slow scan directions have the potential to be accurate.

adu_per_eV = 0.25  ; 1500 ADU per 6000 eV
clen = 0.350
photon_energy = 1000
res = 5000 ; 75 um pixels

dim0 = %
dim1 = ss
dim2 = fs
data = /data/data

mask = /entry_1/instrument_1/detector_1/mask
mask_good = 0x0000
mask_bad = 0xfeff

p0/min_fs = 0
p0/min_ss = 0
p0/max_fs = 511
p0/max_ss = 1023
p0/fs = +0.999999x +0.001590y
p0/ss = +0.001590x +0.999999y
p0/corner_x = -561 
p0/corner_y = -3

p1/min_fs = 512
p1/min_ss = 0
p1/max_fs = 1023
p1/max_ss = 1023
p1/fs = +0.999999x +0.001590y
p1/ss = +0.001590x +0.999999y
p1/corner_x = 0
p1/corner_y = 0

