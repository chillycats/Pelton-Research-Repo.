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
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot

from config import MeasurementType, trimming_threshold
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns
from config import OO_Threshold
from config import blink_bin_width

def blinking(MDICT, Figures, TxtDict, BDICT):
    # Defining the intensity array
    intensity = MDICT['photon_counts']
    # Defining the time bins array
    bins = MDICT['hist_bins']

    # Defining the threshold based on maximum data value
    blinking_thresh = max(intensity) * OO_Threshold

    # Defining the number of times we'll loop through the intensity array 
    # This will keep track of each data point
    num_loops = int(max(intensity)) / blink_bin_width

    # Creating a 2D array that stores all information in the form: 
    # [photon_count, on/off, time_interval]
    intensity_array = np.zeros(num_loops, 3)

    # On states will be classified with a +1 and off states with a -1
