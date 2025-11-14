# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY LIBRARIES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
import struct
import pandas as pd
import numpy as np
import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from typing import Dict, Any, Tuple

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
photons = []   # List to store photon events
markers = []   # List to store marker events  
overflows = [] # List to store overflow events

# Statistics counters
photon_count = 0 
overflow_count = 0
marker_count = 0

def readPTU(filepath):
    # Sets these variables/arrays as global variables
    global photons, markers, overflows
    global photon_count, overflow_count, marker_count
    
    # Reset data arrays and counters for the file
    photons = []
    markers = []
    overflows = []
    photon_count = 0
    overflow_count = 0
    marker_count = 0

    # If no filepath is given
    if filepath is None:
        raise ValueError('ERROR. No file path was given.')
    
    # Reading binary file
    with open(filepath, 'rb') as file:
        # Check if the file is a PTU file
        valid_file = file.read(8).decode('utf-8', errors='ignore').strip('\x00')
        if valid_file != 'PQTTTR':
            raise ValueError('ERROR: This is not a valid PTU file. File type is incorrect.')
        
