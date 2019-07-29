# xfel2146 Offline reconstruction pipeline

1. Run histograms.py (optional)
2. Run litpixels.py to find hits. Results will be saved in scratch/hits
3. Run create_mask.py to mask out cold and hot pixels
4. Create mask with CsPadMaskMakerGUI
5. Run create_dragonfly_det.py to make mask compatible with dragonfly
6. Run hit_to_emc.py to save data in sparse emc format
