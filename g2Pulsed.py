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
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot, normPlot

from config import MeasurementType, trimming_threshold, trimming
from config import Bfilepath, Bduration
from config import bin_width_ps
# g2 Pulsed fitting parameters
from config import Pulsed_Zero_Time_Offset
from config import Pulse_Period_ns
from config import Pfit1
from config import Pulse_Peaks

# Plotting Info. Dicts
from Functions.plotting_config import PExp

def g2Pulsed(MDATA, BDATA, Figures, TxtDict, blinking):
    print("g2 Pulsed measurement selected proceeding with normalization")
    print("and fitting.")
    print("="*60)

    # Checks to make sure sync rate, input rate, and bin width are defined from measurement mode
    if MDATA['mode'] == 'dat':
        raise ValueError('ERROR. Improper measurement mode selected for g2 Pulsed measurement.')

    # Defining all important variables and arrays from Dict of the measurement and background data
    Mcounts = MDATA['photon_counts']
    Mbins = MDATA['hist_bins']
    Mresolution = MDATA['resolution']

    sync_rate = MDATA['sync_rate']
    input_rate = MDATA['input_rate']
    binsize_ns = MDATA['bin_width_ns']
    Mduration_s = MDATA['acquisition_time_s'] 

    print("Duration:", Mduration_s)
    print("Sync rate:", sync_rate)
    print("input rate:", input_rate)

    if blinking == True:
        Mcounts = MDATA['filtered_counts']
        Mbins = MDATA['filtered_bins']

    # - - - - - - - - - - - - - - -
    #      Fitting and Figures
    # - - - - - - - - - - - - - - -

    # Trimming the data - this is different than the lifetime trim (based on a decay)
    # this trim is manually determined by the user in config file
    if trimming == True:
        Mcounts = Mcounts[:trimming_threshold]
        Mbins = Mbins[:trimming_threshold]

    Mcounts = Ng2(Mcounts, 0, Mduration_s, 1, sync_rate, input_rate, binsize_ns)

    print("MAXIMUM VAL:", max(Mcounts))

    Figures.append(normPlot(Mbins, Mcounts))

    print("FINISHED PLOTTING NORMALIZATION PLOT")

    Pfit1_dict = FitPulsed(Mcounts, Mbins, Pfit1, Pulsed_Zero_Time_Offset, Pulse_Peaks)

    print("FINISHED FITTING DATA")

    fitted_curve = Pfit1_dict['fitted curve']
    residuals = Pfit1_dict['residuals']
    y0_fit = Pfit1_dict['parameters'][0]

    print("")
    print("g2(0) =", Pfit1_dict['g2(0)'])
    print("g2 fit period = ", Pfit1_dict['g2 fit period'])
    print("")
    print("="*60)

    Figures.append(plots('g2 Pulsed Fit', Mbins, Mcounts, fitted_curve, residuals))

    # Creating and defining the dict. that will store all important values to be saved in the
    # txt file output
    # General params
    TxtDict['resolution'] = Mresolution
    TxtDict['sync_rate'] = sync_rate
    TxtDict['input_rate'] = input_rate
    TxtDict['bin_width'] = binsize_ns
    # General fit model array of params in order
    TxtDict['model_params'] = ['Pulse Period', 'y0', 'A₁', 'τ₁', 'A₂', 'τ₂', 'R', 'τ0', 'Number of Peaks']
    # Fitting params
    TxtDict['model'] = 'g2 Pulsed'
    TxtDict['fit_params'] = Pfit1_dict['parameters']
    TxtDict['fit_params_errors'] = Pfit1_dict['errors']
    TxtDict['g2(0)'] = Pfit1_dict['g2(0)']
    TxtDict['g2_fit_period'] = Pfit1_dict['g2 fit period']

    print("FINISHED SAVING OUTPUTS TO DICTS - LEAVING g2 PULSED file")

    return Figures, TxtDict