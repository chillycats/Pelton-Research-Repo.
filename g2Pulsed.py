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
from Functions.PTU_Fitting import FitPulsed
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot

from config import MeasurementType, trimming_threshold
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns

# g2 Pulsed fitting parameters
from config import Pulsed_Zero_Time_Offset
from config import Pulse_Period_ns
from config import Pfit1

# Plotting Info. Dicts
from Functions.plotting_config import PExp

def g2Pulsed(MDATA, BDATA):
    print("g2 Pulsed measurement selected proceeding with normalization")
    print("and fitting.")
    print("="*60)

    # Defining the Figures array - this along with a dict of all important info. will be returned
    Figures = MDATA['figures']

    # Defining all important variables and arrays from Dict of the measurement and background data
    Mcounts = MDATA['photon_counts']
    Mbins = MDATA['hist_bins']
    Mresolution = MDATA['resolution']

    """# Checks to make sure sync rate, input rate, and bin width are defined from measurement mode
    if MDATA['mode'] == 'T2' or MDATA['mode'] == 'T3':
        raise ValueError('ERROR. Improper measurement mode selected for g2 Pulsed measurement.')
    
    # Defining important params specific to T2 and T3 mode
    sync_rate = MDATA['sync_rate']
    input_rate = MDATA['input_rate']
    bin_width = MDATA['bin_width']

    # Normalizing and trimming counts then fixing length of time array
    Ncounts = Ng2(counts, 1, Mduration, 1, sync_rate, input_rate, binsize)
    NTcounts, index = threshold_trim_function(Ncounts, trimming_threshold)
    time = bins[:index]"""

    sync_rate = 'N/A'
    input_rate = 'N/A'
    bin_width = 'N/A'

    # - - - - - - - - - - - - - - -
    #      Fitting and Figures
    # - - - - - - - - - - - - - - -

    # Trimming the data - this is different than the lifetime trim (based on a decay)
    # this trim is manually determined by the user in config file
    Mcounts = Mcounts[:trimming_threshold]
    time = Mbins[:trimming_threshold]

    y0 = np.average(Mcounts)
    Pfit1.insert(0, y0)
    Pfit1.insert(0, Pulse_Period_ns)

    Pfit1_dict = FitPulsed(Mcounts, time, Pfit1, Pulsed_Zero_Time_Offset)

    fitted_curve = Pfit1_dict['fitted curve']
    residuals = Pfit1_dict['residuals']
    y0_fit = Pfit1_dict['parameters'][0]

    print("")
    print("g2(0) =", Pfit1_dict['g2(0)'])
    print("g2 fit period = ", Pfit1_dict['g2 fit period'])
    print("")
    print("="*60)

    Figures.append(plots('g2 Pulsed Fit', time, Mcounts, fitted_curve, residuals))

    # Creating and defining the dict. that will store all important values to be saved in the
    # txt file output
    TxtDict = {
        # General params
        'resolution': Mresolution,
        'sync_rate': sync_rate,
        'input_rate': input_rate,
        'bin_width': bin_width,
        # General fit model array of params in order
        'model_params': ['A₁', 'τ₁', 'A₂', 'τ₂', 'R', 'τ0', 'Number of Peaks'],
        # Fitting params
        'model': 'g2 Pulsed',
        'fit_params': Pfit1_dict['parameters'],
        'fit_params_errors': Pfit1_dict['errors'],
        'g2(0)': Pfit1_dict['g2(0)'],
        'g2_fit_period': Pfit1_dict['g2 fit period']
    }

    return Figures, TxtDict