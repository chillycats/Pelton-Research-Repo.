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
photons = []      # List to store photon events
photon_times = [] # List to store dtimes and true times
markers = []      # List to store marker events  
overflows = []    # List to store overflow events

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
        
        # Read file format version
        version = file.read(8).decode('utf-8', errors='ignore').strip('\x00')
        print(f"File Version: {version}")

        # Read header information
        print("="*60)
        print("HEADER INFORMATION")
        print("="*60)
        Header_Data = readHeader(file)

        # Identify the record type (T2 vs T3, which hardware)
        process_record_type()
        print("="*60)

        # Process all data records based on the identified format
        if TTResultFormat_TTTRRecType == rtPicoHarpT3:
            readT3(file)  # Read PicoHarp T3 data
        elif TTResultFormat_TTTRRecType == rtPicoHarpT2:
            readT2(file)  # Read PicoHarp T2 data
        else:
            # Add other formats here as needed
            raise ValueError(f"Unsupported record type: 0x{TTResultFormat_TTTRRecType:08X}")
        
    print(f"Photons decoded: {photon_count}")
    print(f"Marker events: {marker_count}") 
    print(f"Overflow events: {overflow_count}")
    print(f"Total records processed: {TTResult_NumberOfRecords}")
    print("="*60)

    # Convert lists to numpy arrays for better performance
    photons_array = np.array(photons, dtype=[
        ('record_num', 'i4'), ('time_tag', 'i8'), ('channel', 'u1'), 
        ('dtime', 'u2'), ('true_time', 'f8')
    ]) if photons else np.array([])
    
    markers_array = np.array(markers, dtype=[
        ('record_num', 'i4'), ('time_tag', 'i8'), ('markers', 'u1')
    ]) if markers else np.array([])
    
    overflows_array = np.array(overflows, dtype=[
        ('record_num', 'i4'), ('count', 'u2')
    ]) if overflows else np.array([])
    
    # Return all data in a structured dictionary
    return {
        'header': Header_Data,
        'metadata': {
            'record_type': TTResultFormat_TTTRRecType,
            'total_records': TTResult_NumberOfRecords,
            'resolution': MeasDesc_Resolution,
            'global_resolution': MeasDesc_GlobalResolution,
            'is_t2_mode': isT2
        },
        'photons': photons_array,
        'markers': markers_array, 
        'overflows': overflows_array,
        'photon_times': photon_times,
        'statistics': {
            'photons': photon_count,
            'markers': marker_count,
            'overflows': overflow_count
        }
    }

def readHeader(file):
    """
    Read the header section of the PTU T3 file.
    
    The header contains tags in the format:
    - 32 bytes: Tag identifier (string)
    - 4 bytes: Tag index (integer) 
    - 4 bytes: Tag type (integer, see constants above)
    - 8 bytes: Tag value (type depends on tag type)
    
    Args:
        file: File handle of the open PTU file
        
    Returns:
        Dictionary of all header tags and their values
    """

    # Identifying global variables
    global TTResultFormat_TTTRRecType, TTResult_NumberOfRecords
    global MeasDesc_Resolution, MeasDesc_GlobalResolution

    # Creating array that stores header information
    Header_Data = {}

    # Read tags until we find the 'Header_End' tag
    while True:
        # Read tag identifier (32-byte string)
        tag_identifier = file.read(32).decode('utf-8', errors='ignore').strip('\x00')
        if not tag_identifier:
            break  # End of file

        # Read tag index (used for arrays)
        tag_idx = struct.unpack('i', file.read(4))[0]
        
        # Read tag type (determines how to interpret the value)
        tag_type = struct.unpack('I', file.read(4))[0]

        print(f"{tag_identifier:<35}", end='')

        # Process the tag based on its type
        if tag_type == tyEmpty8:
            # Empty tag - just read and discard the value
            value = struct.unpack('q', file.read(8))[0]
            print("<Empty>")
            
        elif tag_type == tyBool8:
            # Boolean value: 0 = False, anything else = True
            value = struct.unpack('q', file.read(8))[0]
            if value == 0:
                print("FALSE")
                Header_Data[tag_identifier] = False
            else:
                print("TRUE")
                Header_Data[tag_identifier] = True
                
        elif tag_type == tyInt8:
            # 64-bit integer value
            value = struct.unpack('q', file.read(8))[0]
            print(f"{value}")
            Header_Data[tag_identifier] = value
            
            # Store important metadata in global variables
            if tag_identifier == 'TTResultFormat_TTTRRecType':
                TTResultFormat_TTTRRecType = value
            elif tag_identifier == 'TTResult_NumberOfRecords':
                TTResult_NumberOfRecords = value
                
        elif tag_type in [tyBitSet64, tyColor8]:
            # Bit set or color value - display as hexadecimal
            value = struct.unpack('q', file.read(8))[0]
            print(f"0x{value:X}")
            Header_Data[tag_identifier] = value
            
        elif tag_type == tyFloat8:
            # 64-bit floating point value
            value = struct.unpack('d', file.read(8))[0]
            print(f"{value:e}")
            Header_Data[tag_identifier] = value
            
            # Store resolution values
            if tag_identifier == 'MeasDesc_Resolution':
                MeasDesc_Resolution = value
            elif tag_identifier == 'MeasDesc_GlobalResolution':
                MeasDesc_GlobalResolution = value
                
        elif tag_type == tyFloat8Array:
            # Array of floats - we just skip over these for now
            tag_int = struct.unpack('q', file.read(8))[0]
            print(f"<Float array with {tag_int // 8} entries>")
            file.seek(tag_int, 1)  # Skip forward by the array size
            
        elif tag_type == tyTDateTime:
            # Date/time value (Windows OLE automation date)
            # Convert from days since 1899-12-30 to Python datetime
            value = struct.unpack('d', file.read(8))[0]
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)
            print(f"{dt}")
            Header_Data[tag_identifier] = dt
            
        elif tag_type == tyAnsiString:
            # ASCII string - read length first, then the string
            str_len = struct.unpack('q', file.read(8))[0]
            value = file.read(str_len).decode('utf-8', errors='ignore').strip('\x00')
            print(f"'{value}'")
            Header_Data[tag_identifier] = value
            
        elif tag_type == tyWideString:
            # Unicode string - read length first, then the string
            str_len = struct.unpack('q', file.read(8))[0]
            value = file.read(str_len).decode('utf-16', errors='ignore').strip('\x00')
            print(f"'{value}'")
            Header_Data[tag_identifier] = value
            
        elif tag_type == tyBinaryBlob:
            # Binary data - just skip over it
            blob_size = struct.unpack('q', file.read(8))[0]
            print(f"<Binary data: {blob_size} bytes>")
            file.seek(blob_size, 1)  # Skip forward by the blob size
            
        else:
            raise ValueError(f"Unknown tag type: 0x{tag_type:08X}")
        
        # Check for end of header
        if tag_identifier == 'Header_End':
            break
    
    return Header_Data

def process_record_type():
    """
    Identify and display the record type based on the header value.
    """

    global TTResultFormat_TTTRRecType, isT2
    
    rec_type = TTResultFormat_TTTRRecType
    
    print("Record type: ", end='')
    
    if rec_type == rtPicoHarpT3:
        isT2 = False
        print("PicoHarp T3 data")
    elif rec_type == rtPicoHarpT2:
        isT2 = True
        print("PicoHarp T2 data")
    elif rec_type == rtHydraHarpT3:
        isT2 = False
        print("HydraHarp V1 T3 data")
    elif rec_type == rtHydraHarpT2:
        isT2 = True
        print("HydraHarp V1 T2 data")
    elif rec_type == rtHydraHarp2T3:
        isT2 = False
        print("HydraHarp V2 T3 data")
    elif rec_type == rtHydraHarp2T2:
        isT2 = True
        print("HydraHarp V2 T2 data")
    elif rec_type == rtTimeHarp260NT3:
        isT2 = False
        print("TimeHarp260N T3 data")
    elif rec_type == rtTimeHarp260NT2:
        isT2 = True
        print("TimeHarp260N T2 data")
    elif rec_type == rtTimeHarp260PT3:
        isT2 = False
        print("TimeHarp260P T3 data")
    elif rec_type == rtTimeHarp260PT2:
        isT2 = True
        print("TimeHarp260P T2 data")
    else:
        raise ValueError(f"Unknown record type: 0x{rec_type:08X}")
    
def readT3(file):
    """
    Read PicoHarp T3 format data into memory arrays.
    
    T3 Record Structure (32 bits):
    +-------------------------------+-------------------------------+
    | Chan (4 bits) | Dtime (12 bits) |         NSync (16 bits)     |
    +-------------------------------+-------------------------------+
    
    Where:
    - Chan: Channel number (1-4 = photons, 15 = special record)
    - Dtime: Time between sync pulse and photon (T3 only)
    - NSync: Sync pulse counter (wraps every 65536)
    
    Special records (Chan=15):
    - If markers=0: Overflow record (NSync counter wrapped)
    - If markers>0: Marker event (external trigger)
    """

    global photons, markers, overflows, photon_count, overflow_count, marker_count
    global photon_times
    
    ofltime = 0           # Overflow correction for NSync
    WRAPAROUND = 65536    # NSync counter wraps at this value
    record_num = 0        # Current record number

    # Process each record in the file
    for i in range(TTResult_NumberOfRecords):
        # Read 32-bit record
        t3_record = struct.unpack('I', file.read(4))[0]
        
        # Extract components using bit operations
        nsync = t3_record & 0xFFFF           # Lower 16 bits: sync counter
        chan = (t3_record >> 28) & 0xF       # Upper 4 bits: channel
        dtime = (t3_record >> 16) & 0xFFF    # Middle 12 bits: dtime (T3 only)
        
        # Apply overflow correction to get absolute sync time
        truensync = ofltime + nsync

        if 1 <= chan <= 4:
            # =============================================================
            # PHOTON EVENT: Regular photon detection on channels 1-4
            # =============================================================
            true_time = truensync * MeasDesc_GlobalResolution * 1e9  # Convert to nanoseconds
        
            photon_times.append((dtime, true_time))

            photons.append((
                record_num,     # Record number in file
                truensync,      # Absolute sync counter value
                chan,           # Channel (1-4)
                dtime,          # Time between sync and photon
                true_time       # Absolute time in nanoseconds
            ))
            photon_count += 1

        elif chan == 15:
            # =============================================================
            # SPECIAL RECORD: Either overflow or marker
            # =============================================================
            markers_val = (t3_record >> 16) & 0xF  # Marker bits
            
            if markers_val == 0:
                # =========================================================
                # OVERFLOW RECORD: Sync counter wrapped around
                # =========================================================
                ofltime += WRAPAROUND  # Add wrap value to overflow correction
                overflows.append((
                    record_num,  # Record number
                    1            # Overflow count (usually 1 per record)
                ))
                overflow_count += 1
            else:
                # =========================================================
                # MARKER EVENT: External trigger or synchronization signal
                # =========================================================
                markers.append((
                    record_num,     # Record number
                    truensync,      # Absolute sync counter value  
                    markers_val     # Marker bitfield
                ))
                marker_count += 1

        else:
            # =============================================================
            # UNKNOWN CHANNEL: Should not happen in valid files
            # =============================================================
            print(f"Warning: Unknown channel {chan} at record {record_num}")
        
        record_num += 1

def readT2(file):
    """
    Read PicoHarp T2 format data into memory arrays.
    
    T2 Record Structure (32 bits):
    +----------------------+----------------------------+
    | Chan (4 bits)        |     T2time (28 bits)       |
    +----------------------+----------------------------+
    
    Where:
    - Chan: Channel number (0-4 = photons, 15 = special record)
    - T2time: Absolute time tag (28 bits, wraps every 210698240)
    
    Special records (Chan=15):
    - If markers=0: Overflow record (T2time counter wrapped)
    - If markers>0: Marker event (external trigger)
    """

    global photons, markers, overflows, photon_count, overflow_count, marker_count, photon_times
    
    ofltime = 0           # Overflow correction for T2time
    WRAPAROUND = 210698240  # T2time counter wraps at this value (as per MATLAB code)
    record_num = 0        # Current record number

    # Process each record in the file
    for i in range(TTResult_NumberOfRecords):
        # Read 32-bit record
        t2_record = struct.unpack('I', file.read(4))[0]
        
        # Extract components using bit operations
        t2time = t2_record & 0xFFFFFFF        # Lower 28 bits: time tag
        chan = (t2_record >> 28) & 0xF        # Upper 4 bits: channel
        
        # Apply overflow correction to get absolute time
        timetag = ofltime + t2time

        if 0 <= chan <= 4:
            # =============================================================
            # PHOTON EVENT: Regular photon detection on channels 0-4
            # =============================================================
            true_time = timetag * MeasDesc_GlobalResolution * 1e9  # Convert to nanoseconds

            photon_times.append(true_time)

            photons.append((
                record_num,     # Record number in file
                timetag,        # Absolute time tag value
                chan,           # Channel (0-4)
                0,              # Dtime is 0 for T2 mode (not applicable)
                true_time       # Absolute time in nanoseconds
            ))
            photon_count += 1

        elif chan == 15:
            # =============================================================
            # SPECIAL RECORD: Either overflow or marker
            # =============================================================
            markers_val = t2_record & 0xF  # Marker bits (lowest 4 bits)
            
            if markers_val == 0:
                # =========================================================
                # OVERFLOW RECORD: Time tag counter wrapped around
                # =========================================================
                ofltime += WRAPAROUND  # Add wrap value to overflow correction
                overflows.append((
                    record_num,  # Record number
                    1            # Overflow count (usually 1 per record)
                ))
                overflow_count += 1
            else:
                # =========================================================
                # MARKER EVENT: External trigger or synchronization signal
                # =========================================================
                markers.append((
                    record_num,     # Record number
                    timetag,        # Absolute time tag value  
                    markers_val     # Marker bitfield
                ))
                marker_count += 1

        else:
            # =============================================================
            # UNKNOWN CHANNEL: Should not happen in valid files
            # =============================================================
            print(f"Warning: Unknown channel {chan} at record {record_num}")
        
        record_num += 1