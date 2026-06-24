# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY LIBRARIES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
import struct
import numpy as np
from scipy import signal
import datetime
import argparse
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from pathlib import Path
from typing import Dict, Any, Tuple

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#        IMPORTING THE NECESSARY FUNCTIONS & VARIABLES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

from Functions.PTU_Normalize import Ng2
from Functions.PTU_Trimmer import threshold_trim_function
from Functions.PTU_Fitting import FitCW
from Functions.PTU_Plotting import intensity_vs_exptime, counts_vs_exptime, rawPlot

from config import MeasurementType, trimming_threshold
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns, dtime_override
from config import OO_Threshold, OO_bin_width_ms

def blinking(MDICT, BDICT, TxtDict, Figures):    
    # Defining the original dtime array
    dtimes = MDICT['dtimes']
    # Defining the absolute time stamp array - in nanoseconds
    # Making sure it's a numpy array
    true_times = np.array(MDICT['true_times'])

    # Converting to miliseconds
    true_times = true_times / 1e6

    # Defining the number of times we need to loop through time array
    loop_num = int(max(true_times)/OO_bin_width_ms) + 1

    # Initializing important arrays
    # Experiment time (ms)
    exp_time = np.zeros((loop_num))
    # Number of counts per time bin
    counts = np.zeros((loop_num))
    # Intensity array (counts per time bin) / bin size
    intensity = np.zeros((loop_num))
    # On/off array (+1 or -1 for each time bin)
    On_Off = np.zeros((loop_num))

    for i in range(loop_num):
        # Determining which entries in the time array are within the window
        window_i = np.logical_and(true_times < (i+1)*OO_bin_width_ms, true_times > i*OO_bin_width_ms)

        # Storing first time window into a time array
        exp_time[i] = OO_bin_width_ms*(i+1)

        # Summing the counts over this time window and storing them in the counts array
        counts[i] = np.sum(window_i)

        # Finding the intensity for this time bin and storing it in the intensity array
        intensity[i] = counts[i] / OO_bin_width_ms

    # Defining the threshold based on maximum data value
    blinking_thresh = max(intensity) * OO_Threshold
    # Creating a mask
    mask = np.zeros(len(true_times), dtype=bool)

    # Filling the mask with proper values
    for i in range(len(true_times)):
        bin_idx = int(true_times[i] / OO_bin_width_ms)  # Convert to ms and bin
        if bin_idx < loop_num:
            if intensity[bin_idx] > blinking_thresh:
                mask[i] = True

    # Filtering the original dtimes array
    OO_dtimes_ns = dtimes[mask]

    # Debugging print statements
    """print("Length of mask:", len(mask))
    print("Number of on states:", sum(mask))
    print("Length of original dtime array:", len(dtimes))
    print("Lenght of the trimmed dtime array", len(OO_dtimes_ns))"""

    # Reconstructing the histogram
    bin_width_ns = bin_width_ps / 1000 # in ns
    # Condition to override user inputted time window
    if dtime_override == True:
        time_window_ns = np.max(dtimes)

    # Create bins from 0 to time_window_ns
    OO_bins = np.arange(0, time_window_ns + bin_width_ns, bin_width_ns)

    # Create histogram
    OO_counts, OO_bin_edges = np.histogram(OO_dtimes_ns, bins=OO_bins)
    
    # Calculate bin centers (for plotting)
    OO_bins = (OO_bin_edges[:-1] + OO_bin_edges[1:]) / 2

    # Converting to seconds
    exp_time = exp_time / 1000
    intensity *= 1000
    blinking_thresh *= 1000

    # Plotting the original data with the threshold
    Figures.append(intensity_vs_exptime(exp_time, intensity, OO_bin_width_ms, np.average(intensity), "Average intensity"))
    Figures.append(intensity_vs_exptime(exp_time, intensity, OO_bin_width_ms, blinking_thresh, "Blinking Threshold"))
    Figures.append(rawPlot(OO_bins, OO_counts))

    # Adding the threshold to the text file dict
    TxtDict['blinking_threshold'] = blinking_thresh
    # Adding the on/off states and the threshold to the MDICT 
    MDICT['blinking_threshold'] = blinking_thresh
    MDICT['filtered_counts'] = OO_counts
    MDICT['filtered_bins'] = OO_bins

    return Figures, TxtDict, MDICT