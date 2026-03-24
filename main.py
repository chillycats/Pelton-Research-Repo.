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

from Functions.PTU_Reader import readPTU
from Functions.PTU_Normalize import NLifetime, Ng2
from Functions.PTU_Trimmer import threshold_trim_function
from Functions.PTU_Fitting import FitLifetime, FitCW, FitPulsed
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot

from config import MeasurementType, trimming_threshold
from config import Mduration
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns

# Lifetime fitting parameters
from config import LNumFits
from config import Lfit1, Lfit2, Lfit3
from config import Generic_Lifetime

# g2 CW Autocorrelation fitting parameters
from config import CW_Zero_Time_Offset
from config import CFit1

# g2 Pulsed fitting parameters
from config import Pulsed_Zero_Time_Offset
from config import Pulse_Period_ns
from config import Pfit1

from Lifetime import Lifetime
from g2Pulsed import g2Pulsed
from g2CWAuto import g2CWAuto

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
    
    # argument for input filepath
    parser.add_argument('--ifile', 
                       required=True,
                       type=str,
                       help='Path to the input PTU file')
    
    # argument for the output file name (program will produce a pdf and txt file
    # with information from analysis with this file name)
    parser.add_argument('--oname',
                       required=True,
                       type=str,
                       help='Name for the output file')
    
    args = parser.parse_args()
    
    # Checks if the file exists
    if not os.path.exists(args.ifile):
        print(f"Error: File '{args.ifile}' does not exist")
        exit(1)

    args = parser.parse_args()
    return args.ifile, args.oname

if __name__ == '__main__':
    # Place to store the figures for output
    Figures = []

    # Stores the filepath and output filename as variables
    filepath, output_filename = parse_arguments()

    # Reads in the data from the file
    Mdata = readPTU(filepath, time_window_ns, bin_width_ps)
    # Reads in the data from the background
    #Bdata = readPTU(Bfilepath)

    # Defines variables for important statistics and metadata from readPTU dict
    # isT2 is Boolean (True = T2 mode; False = T3 mode)
    isT2 = Mdata['metadata']['is_t2_mode']

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
    #       CONVERTING DATA INTO HISTOGRAM FORMAT FOR EACH MODE
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   DAT MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    if Path(filepath).suffix.lower() == '.dat':
        Resolution = Mdata['header']['NS_Per_Channel']
        counts = Mdata['photon_times']
        bins = np.arange(len(counts)) * Resolution
        binsize = Resolution
        Mduration = Mduration

        # Creating a dict unique for dat mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'dat',
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution,
            'figures': Figures
        }

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T3 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    elif isT2 == False:
        # - - - - - - - - - - - - - - -
        # Defining important constants
        # - - - - - - - - - - - - - - -
        DATA = Mdata['photon_times']
        Resolution = Mdata['metadata']['resolution'] * 1E9 # in nanoseconds
        Photon_count = Mdata['statistics']['photons']
        dtimes_ns = np.array([tup[0] for tup in DATA]) * Resolution # in nanoseconds
        photon_times = [tup[1] for tup in DATA] # in nanoseconds

        sync_rate = Mdata['header']['TTResult_SyncRate']
        input_rate = Mdata['header']['TTResult_InputRate']
        Mduration = Mdata['header']['TTResult_StopAfter'] # in miliseconds

        bin_width_ns = bin_width_ps / 1000 # in ns

        # Create bins from 0 to time_window_ns
        n_bins = int(time_window_ns / bin_width_ns)
        bins = np.arange(0, time_window_ns + bin_width_ns, bin_width_ns)

        # Create histogram
        counts, bin_edges = np.histogram(dtimes_ns, bins=bins)
        
        # Calculate bin centers (for plotting)
        bins = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        Mduration = Mdata['header']['MeasDesc_AcquisitionTime'] * 1E6 # in nanoseconds
        DurationRatio = Mduration / Bduration

        # Creating a dict unique for T3 mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'T3',
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution,
            'sync_rate':  Mdata['header']['TTResult_SyncRate'],
            'input_rate': Mdata['header']['TTResult_InputRate'],
            'Meas_duration': Mduration,
            'Duration_ratio': DurationRatio,
            'figures': Figures
        }

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T2 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    elif isT2 == True:
        bins = Mdata['tcspc']['time_axis']
        counts = Mdata['tcspc']['histogram']
        Resolution = Mdata['metadata']['resolution']
        binsize = Mdata['tcspc']['parameters']['bin_width_ps'] * 1000 # in nanseconds

        sync_rate = Mdata['header']['TTResult_SyncRate']
        input_rate = Mdata['header']['TTResult_InputRate']

        Mduration = Mdata['header']['TTResult_StopAfter'] *1E6 # in nanoseconds
        DurationRatio = Mduration / Bduration

        # Creating a dict unique for T2 mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'T3',
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution,
            'sync_rate':  Mdata['header']['TTResult_SyncRate'],
            'input_rate': Mdata['header']['TTResult_InputRate'],
            'Meas_duration': Mduration,
            'Duration_ratio': DurationRatio,
            'figures': Figures
        }

    else:
        raise ValueError('ERROR. Measurement mode is not defined.')

    # = = = = = = = = = = = = = = = = = = = = = = =
    #         DETERMINING MEASUREMENT TYPE
    # = = = = = = = = = = = = = = = = = = = = = = =

    # - - - - - - - - - - - - - - -
    #    No Measurement Selected
    # - - - - - - - - - - - - - - -
    if MeasurementType == 0:
        print("No measurement type selected.")
        print("Plotting data...")
        print("="*60)

        # Plotting the raw data
        Figures.append(rawPlot(bins, counts))

        TxtDict = {
            'Measurement_type': 'no measurement type selected.'
        }

    # - - - - - - - - - - - - - - -
    #     Lifetime Measurement
    # - - - - - - - - - - - - - - -
    elif MeasurementType == 1:
        Figures, TxtDict = Lifetime(MDICT, 0)

    # - - - - - - - - - - - - - - -
    #       g2 CW Measurement
    # - - - - - - - - - - - - - - -
    elif MeasurementType == 2:
        Figures, TxtDict = g2CWAuto(MDICT, 0)

    # - - - - - - - - - - - - - - -
    #     g2 Pulsed Measurement
    # - - - - - - - - - - - - - - -
    elif MeasurementType == 3:
        Figures, TxtDict = g2Pulsed(MDICT, 0)

    else:
        raise ValueError('ERROR. MeasurementType not selected.')
    
    
    pdf_filename = f"{output_filename}.pdf"
    txt_filename = f"{output_filename}.txt"

    # Saving Outputs
    # Plots
    with PdfPages(pdf_filename) as pdf:
        for fig in range(len(Figures)):
            pdf.savefig(Figures[fig], bbox_inches='tight')
            plt.close(fig)

    # Defining the measurement file header dictionary 
    Header = Mdata['header']

    # Variables & Other Important Information
    with open(txt_filename, "w") as file:
        file.write("="*60 + '\n')

        file.write("Measurement file information:" + '\n')
        file.write("Measurement filepath: " + '\n')
        file.write(repr(filepath) + '\n')
        file.write("Measurement date: " + repr(Mdata['header']['File_CreatingDate']) + '\n')
        file.write("Measurement time: " + repr(Mdata['header']['File_CreatingTime']) + '\n')

        file.write("="*60 + '\n')

        file.write("General file parameters:" + '\n')
        file.write("Measurement mode selected: " + repr(MeasurementType) + '\n')
        file.write("Resolution: " + repr(Mdata['header']['NS_Per_Channel']) + '\n')
        file.write("Bin width: " + repr(bin_width_ps) + 'ps' + '\n')
        file.write("Time window: " + repr(time_window_ns) + 'ns' + '\n')
        file.write("Trimming threshold: " + repr(trimming_threshold) + '\n')

        file.write("="*60 + '\n')
        file.write("Measurement type specific parameters:" + '\n')

        for key, value in TxtDict.items():
            file.write(f"{key}: {value}\n")

        file.write("="*60 + '\n')

        file.write('\n')

        file.write("="*60 + '\n')
        file.write("File Header:" + '\n')

        for key, value in Header.items():
            file.write(f"{key}: {value}\n")

        file.write("="*60 + '\n')

        file.close()

    print("")
    print(f"Figures saved to: {pdf_filename}")
    print(f"Additional information saved to: {txt_filename}")
    print("")



