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
from datetime import datetime
from typing import Dict, Any, Tuple

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#        IMPORTING THE NECESSARY FUNCTIONS & VARIABLES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

from Functions.PTU_Reader import readPTU
from Functions.PTU_Normalize import NLifetime, Ng2
from Functions.PTU_Trimmer import threshold_trim_function
from Functions.PTU_Fitting import FitLifetime, FitCW, FitPulsed
from Functions.PTU_Plotting import plots, comparison_plot, rawPlot

from config import MeasurementType, trimming_threshold, base_directory
from config import Mduration
from config import Bfilepath, Bduration
from config import bin_width_ps, time_window_ns, dtime_override
from config import repetition_rate, time_window_ns, trimming

# Blinking parameters
from config import OO_Blinking
from config import OO_Threshold
from config import OO_Measuretype
from config import OO_bin_width_ms
from config import OOLfit, OOPfit

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
from config import Pulse_Peaks
from config import Pfit1

from Lifetime import Lifetime
from g2Pulsed import g2Pulsed
from g2CWAuto import g2CWAuto
from Blinking_Bleaching import blinking

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
    # Initializing the output txt file dict
    TxtDict = {}

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

        if dtime_override == False:
            # Finding the indices of closest value to the time window
            time_window_index = np.where(bins == time_window_ns)
            nearest_index = (np.abs(bins - time_window_ns)).argmin()
            # Trimming data to the specific time window
            bins = bins[:nearest_index]
            counts = counts[:nearest_index]

        # Creating a dict unique for dat mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'dat',
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution
        }

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T3 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    elif isT2 == False:
        # - - - - - - - - - - - - - - -
        # Defining important constants
        # - - - - - - - - - - - - - - -
        DATA = Mdata['photon_times']
        # Important variables for creating the histogram
        Resolution = Mdata['metadata']['resolution'] * 1e9 # in nanoseconds
        # Extracting the data
        Photon_count = Mdata['statistics']['photons']
        dtimes_ns = np.array([tup[0] for tup in DATA]) * Resolution # in nanoseconds
        photon_times = [tup[1] for tup in DATA] # in nanoseconds

        # True time array for blinking code in ms (check)
        true_times = np.array([tup[1] for tup in DATA])

        sync_rate = Mdata['header']['TTResult_SyncRate'] # in Hz
        input_rate = Mdata['header']['TTResult_InputRate'] # in Hz
        Mduration = Mdata['header']['MeasDesc_AcquisitionTime'] # in miliseconds
        Acquisition_Time_s = Mdata['header']['MeasDesc_AcquisitionTime'] / 1000 # in s

        print("Acquisition Time (ns):", Mdata['header']['MeasDesc_AcquisitionTime'] * 1e6)
        print("First True Time (ns):", true_times[0])
        print("Lase True Time (ns):", true_times[len(true_times)-1])

        bin_width_ns = bin_width_ps / 1000

        # Condition to override user inputted time window
        if dtime_override == True:
            time_window_ns = np.max(dtimes_ns)

        # Create bins from 0 to time_window_ns
        n_bins = int((time_window_ns) / bin_width_ns)
        bins = np.arange(0, time_window_ns + bin_width_ns, bin_width_ns)

        # Create histogram
        counts, bin_edges = np.histogram(dtimes_ns, bins=bins)
        
        # Calculate bin centers (for plotting)
        bins = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        Mduration = Mdata['header']['MeasDesc_AcquisitionTime'] * 1E6 # in nanoseconds
        DurationRatio = Mduration / Bduration

        # Print statements for debugging
        """print(f"Min dtime: {np.min(dtimes_ns):.2f} ns")
        print(f"Max dtime: {np.max(dtimes_ns):.2f} ns")
        print(f"Mean counts per bin: {np.mean(counts):.2f}")
        print(f"Max counts in any bin: {np.max(counts)}")"""

        # Creating a dict unique for T3 mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'T3',
            'true_times': true_times,
            'dtimes': dtimes_ns,
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution,
            'sync_rate':  Mdata['header']['TTResult_SyncRate'],
            'input_rate': Mdata['header']['TTResult_InputRate'],
            'acquisition_time_s': Acquisition_Time_s,
            'bin_width_ns': bin_width_ns,
            'Meas_duration': Mduration,
            'Duration_ratio': DurationRatio
        }

    # = = = = = = = = = = = = = = = = = = = = = = =
    #                   T2 MODE
    # = = = = = = = = = = = = = = = = = = = = = = =
    elif isT2 == True:
        bins = Mdata['tcspc']['time_axis']
        counts = Mdata['tcspc']['histogram']
        Resolution = Mdata['metadata']['resolution']
        binsize = Mdata['tcspc']['parameters']['bin_width_ps'] / 1000 # in nanseconds

        sync_rate = Mdata['header']['TTResult_SyncRate']
        input_rate = Mdata['header']['TTResult_InputRate']
        Acquisition_Time_ms = Mdata['header']['MeasDesc_AcquisitionTime'] / 1000 # in s

        Mduration = Mdata['header']['MeasDesc_AcquisitionTime'] # in miliseconds
        DurationRatio = Mduration / Bduration

        true_times = Mdata['tcspc']['photon_times']

        print(len(counts))
        print(len(Mdata['photon_times']))

        print("Acquisition Time (s):", Mdata['header']['MeasDesc_AcquisitionTime'] / 1000)
        print("First True Time (s):", true_times[0]*1e-9)
        print("Lase True Time (s):", true_times[len(true_times)-1]*1e-9)
        print("")

        
        channels = Mdata['T2channel']
        ch1 = []
        ch2 = []

        for i in range(len(channels)):
            if channels[i] == 1:
                ch1.append(1)
            elif channels[i] == 0:
                ch2.append(2)

        print("Numer of counts in channel 0:", np.sum(ch2))
        print("Average count rate in channel 0 (counts/s):", np.sum(ch2)/(true_times[len(true_times)-1]*1e-9))
        print("Sync rate from header:", sync_rate)
        print("")
        print("Number of counts in channel 1:", np.sum(ch1))
        print("Average count rate in channel 1:", np.sum(ch1)/(true_times[len(true_times)-1]*1e-9))
        print("Input rate from header:", input_rate)

        # Creating a dict unique for T2 mode that contains all important info. (important for txt file)
        # This dict will be passed to a separate file for each specific measurement type
        MDICT = {
            'mode': 'T3',
            'true_times': true_times,
            'photon_counts': counts,
            'hist_bins': bins,
            'resolution': Resolution,
            #'sync_rate':  Mdata['header']['TTResult_SyncRate'],
            'sync_rate': np.sum(ch2)/(true_times[len(true_times)-1]*1e-9),
            #'input_rate': Mdata['header']['TTResult_InputRate'],
            'input_rate': np.sum(ch1)/(true_times[len(true_times)-1]*1e-9),
            #'acquisition_time_s': Acquisition_Time_ms,
            'acquisition_time_s': true_times[len(true_times)-1]*1e-9,
            'bin_width_ns': binsize,
            'Meas_duration': Mduration,
            'Duration_ratio': DurationRatio
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
        # Plotting the raw data
        Figures.append(rawPlot(bins, counts))

        blink_lifetime = False

        Figures, TxtDict = Lifetime(MDICT, 0, Figures, TxtDict, blink_lifetime)

    # - - - - - - - - - - - - - - -
    #       g2 CW Measurement
    # - - - - - - - - - - - - - - -
    elif MeasurementType == 2:
        # Plotting the raw data
        Figures.append(rawPlot(bins, counts))

        Figures, TxtDict = g2CWAuto(MDICT, 0, Figures, TxtDict)

    # - - - - - - - - - - - - - - -
    #     g2 Pulsed Measurement
    # - - - - - - - - - - - - - - -
    elif MeasurementType == 3:
        # Plotting the raw data
        Figures.append(rawPlot(bins, counts))
        
        Figures, TxtDict = g2Pulsed(MDICT, 0, Figures, TxtDict, blinking=False)

    else:
        raise ValueError('ERROR. MeasurementType not selected.')
    
    # = = = = = = = = = = = = = = = = = = = = = = =
    #            BLINKING & BLEACHING
    # = = = = = = = = = = = = = = = = = = = = = = =

    if OO_Blinking == 1:
        # Making sure the file is in the right mode
        if Path(filepath).suffix.lower() == '.dat' or isT2 == True:
            raise ValueError('ERROR. Cannot execute blinking code for T2 mode/.dat file')
        
        Figures, TxtDict, MDICT = blinking(MDICT, 0, TxtDict, Figures)

        # If we are doing a blinking analysis on a lifetime measurement
        if OO_Measuretype == 0:
            Figures, TxtDict = Lifetime(MDICT, 0, Figures, TxtDict, blinking=True)
        # If we are doing a blinking analysis on a g2 pulsed measurement
        elif OO_Measuretype == 1:
            Figures, TxtDict = g2Pulsed(MDICT, 0, Figures, TxtDict, blinking=True)

    # = = = = = = = = = = = = = = = = = = = = = = =
    #          CREATING OUTPUT PDF & TXT
    # = = = = = = = = = = = = = = = = = = = = = = =

    # Creating a dict. of all the config parameters to save to
    # the output .txt file
    config_dict = {
        'directory_saved_to': base_directory,
        'measurement_type': MeasurementType,
        'background_filepath': Bfilepath,
        'background_duration': Bduration,
        'measurement_duration': Mduration,
        'bin_width_ps': bin_width_ps,
        'laser_repetition_rate': repetition_rate,
        'time_window_ns': time_window_ns,
        'dtime_override': dtime_override,
        'trimming_threshold': trimming_threshold,
        'trimming': trimming,
        'number_of_lifetime_fits': LNumFits,
        'first_lifetime_fit': Lfit1,
        'second_lifetime_fit': Lfit2,
        'third_lifetime_fit': Lfit3,
        'autocorrelation_fit_time_offset_ns': CW_Zero_Time_Offset,
        'cw_autocorrelation_fit': CFit1,
        'pulsed_fit_pulse period_ns': Pulse_Period_ns,
        'pulsed_fit_time_offset_ns': Pulsed_Zero_Time_Offset,
        'pulsed_fit': Pfit1,
        'num_of_peaks': Pulse_Peaks,
        'blinking_analysis': OO_Blinking,
        'blinking_threshold': OO_Threshold,
        'blinking_measurement_type': OO_Measuretype,
        'blinking_bin_width_ms': OO_bin_width_ms,
        'blinking_lifetime_fit': OOLfit,
        'blinking_pulsed_fit': OOPfit
    }

    # Getting the time 
    timestamp = datetime.now().strftime("%m-%d-%Y")
    output_directory = os.path.join(base_directory, timestamp)

    # Creating a folder titled with current date
    os.makedirs(output_directory, exist_ok=True)
    print(f"Saving to folder: {output_directory}")

    # Combine directory with filename
    pdf_filename = os.path.join(output_directory, f"{output_filename}.pdf")
    txt_filename = os.path.join(output_directory, f"{output_filename}.txt")

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
        try: 
            file.write("Measurement date: " + repr(Mdata['header']['File_CreatingDate']) + '\n')
            file.write("Measurement time: " + repr(Mdata['header']['File_CreatingTime']) + '\n')
        except:
            print("No measurement date/time found.")

        # Saving all the config parameter values
        file.write("="*60 + '\n')
        file.write("Config parameters:" + '\n')
        
        for key, value in config_dict.items():
            file.write(f"{key}: {value}\n")
        
        file.write("="*60 + '\n')
        file.write('\n')

        # Saving parameters specific to the fitting
        file.write("="*60 + '\n')
        file.write("Measurement type specific parameters:" + '\n')

        for key, value in TxtDict.items():
            file.write(f"{key}: {value}\n")

        file.write("="*60 + '\n')
        file.write('\n')

        # Writing the original header file into the txt file
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



