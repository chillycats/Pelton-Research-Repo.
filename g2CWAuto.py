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
from config import bin_width_ps
# g2 Pulsed fitting parameters
from config import CW_Zero_Time_Offset
from config import Pulse_Period_ns
from config import CFit1

def g2CWAuto(MDATA, BDATA, Figures, TxtDict):
    print("g2 Pulsed measurement selected proceeding with normalization")
    print("and fitting.")
    print("="*60)

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


    # Normalizing and trimming counts then fixing length of time array
    #Ncounts = Ng2(counts, 1, Mduration, 1, sync_rate, input_rate, binsize)
    Mcounts, index = threshold_trim_function(Mcounts, trimming_threshold)
    time = Mbins[:index]

    Figures.append(rawPlot(time, Mcounts))

    # - - - - - - - - - - - - - - -
    #      Fitting and Figures
    # - - - - - - - - - - - - - - -

    CW_Fit1_Dict = FitCW(Mcounts, time, CFit1)

    fitted_curve = CW_Fit1_Dict['fitted curve']
    residuals = CW_Fit1_Dict['residuals']

    Figures.append(plots('CW Autocorrelation Fit', time, Mcounts, fitted_curve, residuals))

    # Creating and defining the dict. that will store all important values to be saved in the
    # txt file output

    # General params
    TxtDict['resolution'] = Mresolution
    TxtDict['sync_rate'] = sync_rate
    TxtDict['input_rate'] = input_rate
    TxtDict['bin_width'] = bin_width
    # General fit model array of params in order
    TxtDict['model_params'] = ['A₁', 'τ₁']
    # Fitting params
    TxtDict['model'] = 'g2 CW Autocorrelation'
    TxtDict['fit_params'] = CW_Fit1_Dict['parameters']
    TxtDict['fit_params_errors'] = CW_Fit1_Dict['errors']
    
    return Figures, TxtDict