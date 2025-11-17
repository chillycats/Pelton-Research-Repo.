# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY LIBRARIES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
import struct
import numpy as np
import datetime
import argparse
import os

from pathlib import Path
from typing import Dict, Any, Tuple

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY FUNCTIONS
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

from PTU_Reader import readPTU

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               INITIALIZING VARIABLES AND CONSTANTS
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

# Header Variables
TTResultFormat_TTTRRecType = 0      # Type of data records (T2 vs T3, hardware type)
TTResult_NumberOfRecords = 0        # Total number of data records in file
MeasDesc_Resolution = 0.0           # Time resolution for dtime (T3 only)
MeasDesc_GlobalResolution = 0.0     # Global time resolution for time tags
isT2 = False                        # Flag indicating T2 mode (True) vs T3 mode (False)

# Arrays to store the decoded data 
photons = []      # List to store photon events
photon_times = [] # List to store dtimes and true times
markers = []      # List to store marker events  
overflows = []    # List to store overflow events

# Statistics counters
photon_count = 0 
overflow_count = 0
marker_count = 0

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
    
    # Validate file exists
    if not os.path.exists(args.ifile):
        print(f"Error: File '{args.filepath}' does not exist")
        exit(1)

    args = parser.parse_args()
    return args.ifile, args.oname

if __name__ == '__main__':
    # Stores the filepath and output filename as variables
    filepath, output_filename = parse_arguments()

    # Reads in the data from the file
    data = readPTU(filepath)

    # Defines variables for important statistics and metadata from readPTU dict
    Resolution = data['metadata']['resolution']
    Photon_count = data['statistics']['photons']
    isT2 = data['metadata']['is_t2_mode']

    # If in T3 mode convert photon data into histogram format
    if isT2 == False:
        DATA = data['photon_times']
        dtimes = [tup[0] for tup in DATA]
        photon_times = [tup[1] for tup in DATA]
        
    # If in T2 mode define data as the array of true times
    else:
        DATA = data['photon_times']