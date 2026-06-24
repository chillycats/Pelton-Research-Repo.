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
from config import bin_width_ps
# Lifetime fitting parameters
from config import LNumFits
from config import Lfit1, Lfit2, Lfit3, OOLfit
from config import Generic_Lifetime

# Plotting Info. Dicts
from Functions.plotting_config import LExp, LBiExp, LTriExp

def Lifetime(MDATA, BDATA, Figures, TxtDict, blinking):
    global LNumFits, Lfit1

    print("Lifetime measurement selected proceeding with normalization")
    print("and fitting.")
    print("="*60)

    # Defining all important variables and arrays from Dict of the measurement and background data
    Mcounts = MDATA['photon_counts']
    Mbins = MDATA['hist_bins']
    Mresolution = MDATA['resolution']

    if blinking == True:
        Mcounts = MDATA['filtered_counts']
        Mbins = MDATA['filtered_bins']
        LNumFits = 1
        Lfit1 = OOLfit

    """# Defining special params specific to T2 and T3 mode
    if MDATA['mode'] == 'T2' or MDATA['mode'] == 'T3':
        sync_rate = MDATA['sync_rate']
        input_rate = MDATA['input_rate']
        bin_width = MDATA['bin_width']"""

    # Normalizing and trimming counts then fixing len time array
    Ncounts = NLifetime(Mcounts, 0, 1)
    NTcounts, index = threshold_trim_function(Ncounts, trimming_threshold)
    time = Mbins[:index]

    Figures.append(rawPlot(time, NTcounts))

    # - - - - - - - - - - - - - - -
    #      Fitting and Figures
    # - - - - - - - - - - - - - - -
    # Only one fit chosen
    if LNumFits == 1:
        Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
        Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
        
        # Place holder variables
        Lfit2_dict = {
            'model_type': 'N/A',
            'parameters': 'N/A',
            'errors': 'N/A'
        }

        Lfit3_dict = {
            'model_type': 'N/A',
            'parameters': 'N/A',
            'errors': 'N/A'
        }

    # Two fits chosen - adds a comparison plot figure
    elif LNumFits == 2:
        Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
        Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
        Lfit2_dict = FitLifetime(NTcounts, time, Lfit2)
        Figures.append(plots(Lfit2_dict['model_type'], time, NTcounts, Lfit2_dict['normalized_fit'], Lfit2_dict['residuals']))
        
        # Place holder variables
        Lfit3_dict = {
            'model_type': 'N/A',
            'parameters': 'N/A',
            'errors': 'N/A'
        }
        
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

    # Defining new keys for the dict. that will store all important values to be saved in the
    # txt file output
    if blinking == True:
        TxtDict['blinking_lifetime_fit'] = 'True'
        TxtDict['blinking_resolution'] = Mresolution
        TxtDict['blinking_num_of_fits'] = LNumFits
        # General fit model array of params in order
        TxtDict['blinking_model_params'] = ['A₁', 'τ₁', 'A₂', 'τ₂', 'A₃', 'τ₃']
        # Lifetime fit 1 
        TxtDict['blinking_lifetime_model1'] = Lfit1_dict['model_type']
        TxtDict['blinking_fit1_params'] = Lfit1_dict['parameters']
        TxtDict['blinking_fit1_params_er'] = Lfit1_dict['errors']
        # Lifetime fit 2
        TxtDict['blinking_lifetime_model2'] = Lfit2_dict['model_type']
        TxtDict['blinking_fit2_params'] = Lfit2_dict['parameters']
        TxtDict['blinking_fit2_params_er'] = Lfit2_dict['errors']
        # Lifetime fit 3
        TxtDict['blinking_lifetime_model3'] =  Lfit3_dict['model_type']
        TxtDict['blinking_fit3_params'] = Lfit3_dict['parameters']
        TxtDict['blinking_fit3_params_er'] = Lfit3_dict['errors']
    else:
        TxtDict['blinking_lifetime_fit'] = 'False'
        TxtDict['resolution'] = Mresolution
        TxtDict['num_of_fits'] = LNumFits
        # General fit model array of params in order
        TxtDict['model_params'] = ['A₁', 'τ₁', 'A₂', 'τ₂', 'A₃', 'τ₃']
        # Lifetime fit 1 
        TxtDict['lifetime_model1'] = Lfit1_dict['model_type']
        TxtDict['fit1_params'] = Lfit1_dict['parameters']
        TxtDict['fit1_params_er'] = Lfit1_dict['errors']
        # Lifetime fit 2
        TxtDict['lifetime_model2'] = Lfit2_dict['model_type']
        TxtDict['fit2_params'] = Lfit2_dict['parameters']
        TxtDict['fit2_params_er'] = Lfit2_dict['errors']
        # Lifetime fit 3
        TxtDict['lifetime_model3'] =  Lfit3_dict['model_type']
        TxtDict['fit3_params'] = Lfit3_dict['parameters']
        TxtDict['fit3_params_er'] = Lfit3_dict['errors']

    return Figures, TxtDict