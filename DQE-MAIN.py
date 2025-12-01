# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY LIBRARIES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
import struct
import numpy as np
import datetime
import argparse
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from pathlib import Path
from typing import Dict, Any, Tuple

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY FUNCTIONS
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

from Functions.PTU_Reader import readPTU
from Functions.PTU_Normalize import T2_NLifetime
from Functions.PTU_Trimmer import threshold_trim_function
from Functions.PTU_Fitting import FitLifetime
from Functions.PTU_Plotting import plots, comparison_plot

from config import MeasurementType, trimming_threshold
from config import bckgrd_filepath, bckgrd_duration

# Lifetime fitting parameters
from config import LNumFits
from config import Lfit1, Lfit2, Lfit3

# CW g2 fitting parameters

# Plotting Info. Dicts
from Functions.plotting_config import LExp, LBiExp, LTriExp

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                    INITIALIZING CONSTANTS
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# Identifying different tag types
tyEmpty8 = 0xFFFF0008
tyBool8 = 0x00000008
tyInt8 = 0x10000008
tyBitSet64 = 0x11000008
tyColor8 = 0x12000008
tyFloat8 = 0x20000008
tyTDateTime = 0x21000008
tyFloat8Array = 0x2001FFFF
tyAnsiString = 0x4001FFFF
tyWideString = 0x4002FFFF
tyBinaryBlob = 0xFFFFFFFF

# Record Types - identify the specific hardware and data format

# We only need the PicoHarpT3 and maybe PicoHarpT2, but if someone wants to expand the code
# to include other hardware then you would need to know which record type the hardward corresponds to
rtPicoHarpT3 = 0x00010303
rtPicoHarpT2 = 0x00010203
rtHydraHarpT3 = 0x00010304
rtHydraHarpT2 = 0x00010204
rtHydraHarp2T3 = 0x01010304
rtHydraHarp2T2 = 0x01010204
rtTimeHarp260NT3 = 0x00010305
rtTimeHarp260NT2 = 0x00010205
rtTimeHarp260PT3 = 0x00010306
rtTimeHarp260PT2 = 0x00010206

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                           MAIN PROGRAM
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

def parse_arguments():
    """
    Parses command line arguments and returns all arguments.
    """
    parser = argparse.ArgumentParser(
        description='Process .ptu data files'
    )
    
    parser.add_argument('--ifile', 
                       required=True,
                       type=str,
                       help='Path to the input PTU file')
    
    parser.add_argument('--oname',
                       required=True,
                       type=str,
                       help='Name for the output file')
    
    args = parser.parse_args()
    
    # Checks if the file exists
    if not os.path.exists(args.ifile):
        print(f"Error: File '{args.filepath}' does not exist")
        exit(1)

    args = parser.parse_args()
    return args.ifile, args.oname

if __name__ == '__main__':
    # Place to store the figures for output
    Figures = []

    # Stores the filepath and output filename as variables
    filepath, output_filename = parse_arguments()

    # Reads in the data from the file
    Mdata = readPTU(filepath)

    # Defines variables for important statistics and metadata from readPTU dict
    # isT2 is Boolean (True = T2 mode; False = T3 mode)
    isT2 = Mdata['metadata']['is_t2_mode']

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T3 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    if isT2 == False:
        # - - - - - - - - - - - - - - -
        # Defining important constants
        # - - - - - - - - - - - - - - -
        DATA = Mdata['photon_times']
        Resolution = Mdata['metadata']['resolution']
        Photon_count = Mdata['statistics']['photons']
        dtimes = [tup[0] for tup in DATA]
        photon_times = [tup[1] for tup in DATA]
        MeasurementDuration = Mdata['header']['MeasDesc_StopAt']
        DurationRatio = MeasurementDuration / bckgrd_duration

        Offset_time = .02/(1E9*Resolution) 

        # - - - - - - - - - - - - - - -
        # Converting Data to Histogram
        # - - - - - - - - - - - - - - -
        data_step = 6
        bin_size = data_step*Resolution
        binstemp=np.arange(Offset_time, np.max(dtimes),data_step)

        hist_n,hist_bins=np.histogram(dtimes,binstemp)

        hist_bins_temp=np.zeros((len(hist_bins)-1,2))
        hist_bins_temp[:,0]=hist_bins[1:]
        
        # take the midpoints of each time delay bin 
        hist_bins_temp[:,0]=0.5*(hist_bins[:len(hist_bins)-1]+hist_bins_temp[:,0])
        
        # convert delay time bins to nanoseconds
        hist_bins_temp[:,0]=hist_bins_temp[:,0]*(1E9*Resolution)
        # put counts for each delay time into second column
        hist_bins_temp[:,1]=hist_n
        counts = hist_bins_temp[:,1] # photon counts
        bins = hist_bins_temp[:,0]   # bin midpoints, delay times

        # - - - - - - - - - - - - - - -
        # Depending on Measurement Type
        # - - - - - - - - - - - - - - -

        if MeasurementType == 0:
            print("No measurement type selected.")
            print("")
            print("Plotting data...")

        elif MeasurementType == 1:
            print("Lifetime measurement selected proceeding with normalization and fitting.")
            print("="*60)

            Ncounts = T2_NLifetime(counts, 0, DurationRatio)
            NTcounts = threshold_trim_function(Ncounts, trimming_threshold)
            time = np.arange(0, len(NTcounts) * Resolution*1E9, Resolution*1E9)

            if LNumFits == 1:
                Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
                Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
                
            elif LNumFits == 2:
                Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
                Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
                Lfit2_dict = FitLifetime(NTcounts, time, Lfit2)
                Figures.append(plots(Lfit2_dict['model_type'], time, NTcounts, Lfit2_dict['normalized_fit'], Lfit2_dict['residuals']))
                
                Figures.append(comparison_plot(3, time, NTcounts, Lfit1_dict['model_type'], Lfit1_dict['normalized_fit'], Lfit2_dict['model_type'], Lfit2_dict['normalized_fit']))
                

            elif LNumFits == 3:
                Lfit1_dict = FitLifetime(NTcounts, time, Lfit1)
                Figures.append(plots(Lfit1_dict['model_type'], time, NTcounts, Lfit1_dict['normalized_fit'], Lfit1_dict['residuals']))
                Lfit2_dict = FitLifetime(NTcounts, time, Lfit2)
                Figures.append(plots(Lfit2_dict['model_type'], time, NTcounts, Lfit2_dict['normalized_fit'], Lfit2_dict['residuals']))
                Lfit3_dict = FitLifetime(NTcounts, time, Lfit3)
                Figures.append(plots(Lfit3_dict['model_type'], time, NTcounts, Lfit3_dict['normalized_fit'], Lfit3_dict['residuals']))

                Figures.append(comparison_plot(3, time, NTcounts, Lfit1_dict['model_type'], Lfit1_dict['normalized_fit'], Lfit2_dict['model_type'], Lfit2_dict['normalized_fit'], Lfit3_dict['model_type'], Lfit3_dict['normalized_fit']))



            plt.figure()
            plt.plot(time,NTcounts,'o')
            plt.yscale('log')
            plt.xlabel('dtime, in ns')
            plt.ylabel('intensity, counts')
            plt.grid(True)


        elif MeasurementType == 2:
            print("g2 CW Autocorrelation measurement selected proceeding with normalization and fitting.")

        elif MeasurementType == 3:
            print("g2 Pulsed measurement selected proceeding with normalization and fitting.")

        else:
            raise ValueError('ERROR. MeasurementType not selected.')
        

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T2 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    elif isT2 == True:
        DATA = Mdata['photon_times']
        Resolution = Mdata['metadata']['resolution']
        MeasurementDuration = Mdata['header']['MeasDesc_StopAt']
        DurationRatio = MeasurementDuration / bckgrd_duration

        # - - - - - - - - - - - - - - -
        # Depending on Measurement Type
        # - - - - - - - - - - - - - - -

        if MeasurementType == 0:
            print("No measurement type selected.")
            print("")
            print("Plotting data...")

        elif MeasurementType == 1:
            print("Lifetime measurement selected proceeding with normalization and fitting.")

        elif MeasurementType == 2:
            print("g2 CW Autocorrelation measurement selected proceeding with normalization and fitting.")

        elif MeasurementType == 3:
            print("g2 Pulsed measurement selected proceeding with normalization and fitting.")

        else:
            raise ValueError('ERROR. MeasurementType not selected.')
    
    else:
        raise ValueError('ERROR. isT2 variable not defined.')
    
    pdf_filename = f"{output_filename}.pdf"

    # Saving Outputs
    with PdfPages(pdf_filename) as pdf:
        for fig in range(len(Figures)):
            pdf.savefig(Figures[fig], bbox_inches='tight')
            plt.close(fig)

    print("")
    print(f"Figures saved to: {pdf_filename}")



