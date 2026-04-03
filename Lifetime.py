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

from Functions.PTU_Normalize import NLifetime
from Functions.PTU_Trimmer import threshold_trim_function
from Functions.PTU_Fitting import FitLifetime
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot

from config import MeasurementType, trimming_threshold
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns

# Lifetime fitting parameters
from config import LNumFits
from config import Lfit1, Lfit2, Lfit3
from config import Generic_Lifetime

# Plotting Info. Dicts
from Functions.plotting_config import LExp, LBiExp, LTriExp

def Lifetime(MDATA, BDATA):
    print("Lifetime measurement selected proceeding with normalization")
    print("and fitting.")
    print("="*60)

    # Defining the Figures array - this along with a dict of all important info. will be returned
    Figures = MDATA['figures']

    # Defining all important variables and arrays from Dict of the measurement and background data
    Mcounts = MDATA['photon_counts']
    Mbins = MDATA['hist_bins']
    Mresolution = MDATA['resolution']

    # Defining special params specific to T2 and T3 mode
    if MDATA['mode'] == 'T2' or MDATA['mode'] == 'T3':
        sync_rate = MDATA['sync_rate']
        input_rate = MDATA['input_rate']
        bin_width = MDATA['bin_width']

    # Normalizing and trimming counts then fixing len time array
    Ncounts = NLifetime(Mcounts, 0, 1)
    NTcounts, index = threshold_trim_function(Ncounts, trimming_threshold)
    time = Mbins[:index]

    # - - - - - - - - - - - - - - -
    #      Fitting and Figures
    # - - - - - - - - - - - - - - -
    # Only one fit chosen
    if LNumFits == 1:
        Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
        Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
        
    # Two fits chosen - adds a comparison plot figure
    elif LNumFits == 2:
        Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
        Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
        Lfit2_dict = FitLifetime(NTcounts, time, Lfit2)
        Figures.append(plots(Lfit2_dict['model_type'], time, NTcounts, Lfit2_dict['normalized_fit'], Lfit2_dict['residuals']))
        
        Figures.append(comparison_plot(2, time, NTcounts, Lfit1_dict['model_type'], Lfit1_dict['normalized_fit'], Lfit2_dict['model_type'], Lfit2_dict['normalized_fit'], 1, 1))
        
    # Three fits are chosen
    elif LNumFits == 3:
        Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
        Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
        Lfit2_dict = FitLifetime(NTcounts, time, Lfit2)
        Figures.append(plots(Lfit2_dict['model_type'], time, NTcounts, Lfit2_dict['normalized_fit'], Lfit2_dict['residuals']))
        Lfit3_dict = FitLifetime(NTcounts, time, Lfit3)
        Figures.append(plots(Lfit3_dict['model_type'], time, NTcounts, Lfit3_dict['normalized_fit'], Lfit3_dict['residuals']))

        Figures.append(comparison_plot(3, time, NTcounts, Lfit1_dict['model_type'], Lfit1_dict['normalized_fit'], Lfit2_dict['model_type'], Lfit2_dict['normalized_fit'], Lfit3_dict['model_type'], Lfit3_dict['normalized_fit']))

    # Creating and defining the dict. that will store all important values to be saved in the
    # txt file output
    TxtDict = {
        'resolution': Mresolution,
        'num_of_fits': LNumFits,
        # General fit model array of params in order
        'model_params': ['A₁', 'τ₁', 'A₂', 'τ₂', 'A₃', 'τ₃'],
        # Lifetime fit 1 
        'lifetime_model1': Lfit1_dict['model_type'],
        'fit1_params': Lfit1_dict['parameters'],
        'fit1_params_er': Lfit1_dict['errors'],
        # Lifetime fit 2
        'lifetime_model2': Lfit2_dict['model_type'],
        'fit2_params': Lfit2_dict['parameters'],
        'fit2_params_er': Lfit2_dict['errors'],
        # Lifetime fit 3
        'lifetime_model3': Lfit3_dict['model_type'],
        'fit3_params': Lfit3_dict['parameters'],
        'fit3_params_er': Lfit3_dict['errors'],
    }

    return Figures, TxtDict