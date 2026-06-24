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
photon_times = [] # List to store dtimes and true times (T3) or true times (T2)
markers = []      # List to store marker events  
overflows = []    # List to store overflow events
channel = []      # List to store channel number for T2 mode
# Statistics counters
photon_count = 0 
overflow_count = 0
marker_count = 0

def readPTU(filepath, time_window_ns=50, bin_width_ps=25,
            sync_channel=0, signal_channel=1):
    """
    Read PTU file with optional TCSPC histogramming for T2 mode.
    
    Parameters:
    -----------
    filepath : str
        Path to the PTU file
    sync_channel : int (default=0)
        Channel number for sync/reference (laser pulses) - T2 only
    signal_channel : int (default=1)
        Channel number for signal (detected photons) - T2 only
    time_window_ns : float (default=50)
        Time window for histogram in nanoseconds - T2 only
    bin_width_ps : float (default=25)
        Bin width in picoseconds - T2 only
        
    Returns:
    --------
    Dictionary containing all data with TCSPC histogram for T2 files
    """
    
    # Sets these variables/arrays as global variables
    global photons, markers, overflows
    global photon_count, overflow_count, marker_count
    global TTResultFormat_TTTRRecType, TTResult_NumberOfRecords
    global MeasDesc_Resolution, MeasDesc_GlobalResolution, isT2

    
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
    
    if Path(filepath).suffix.lower() == '.dat':
        return readDAT(filepath)
    
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

        # Variable to store T2 histogram data if applicable
        t2_histogram_data = None
        
        # Process all data records based on the identified format
        if TTResultFormat_TTTRRecType == rtPicoHarpT3:
            readT3(file)  # Read PicoHarp T3 data
            result_type = 'T3'
            
        elif TTResultFormat_TTTRRecType == rtPicoHarpT2:
            # Debug file position
            current_pos = file.tell()
            file.seek(0, 2)  # Go to end
            file_size = file.tell()
            file.seek(current_pos)  # Go back
            
            bytes_remaining = file_size - current_pos
            bytes_needed = TTResult_NumberOfRecords * 4
            
            """print(f"\n=== FILE DEBUG INFO ===")
            print(f"File size: {file_size} bytes")
            print(f"Current position: {current_pos} bytes")
            print(f"Bytes remaining: {bytes_remaining}")
            print(f"Expected records: {TTResult_NumberOfRecords}")
            print(f"Bytes needed: {bytes_needed}")
            print(f"Actual records possible: {bytes_remaining // 4}")"""
            
            if bytes_remaining < bytes_needed:
                print(f"WARNING: File is too short! Will only read {bytes_remaining // 4} records")
                # Override the record count
                TTResult_NumberOfRecords = bytes_remaining // 4

            # CAPTURE THE RETURN VALUE from readT2
            t2_histogram_data = readT2(file, sync_channel, signal_channel, 
                                      time_window_ns, bin_width_ps)
            result_type = 'T2'
            
        else:
            # Add other formats here as needed
            raise ValueError(f"Unsupported record type: 0x{TTResultFormat_TTTRRecType:08X}")
        
    print(f"Photons decoded: {photon_count}")
    print(f"Marker events: {marker_count}") 
    print(f"Overflow events: {overflow_count}")
    print(f"Total records processed: {TTResult_NumberOfRecords}")
    print("="*60)

    # Build the return dictionary based on result type
    if result_type == 'T3':
        # For T3, use global variables that were modified by readT3
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
        
        result_dict = {
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
            'T2channel': channel,
            'statistics': {
                'photons': photon_count,
                'markers': marker_count,
                'overflows': overflow_count
            }
        }
        
    elif result_type == 'T2':
        # For T2, use the data returned by readT2
        photons_array = np.array(t2_histogram_data['photons'], dtype=[
            ('record_num', 'i4'), ('time_tag', 'i8'), ('channel', 'u1'), 
            ('dtime', 'u2'), ('true_time', 'f8')
        ]) if t2_histogram_data['photons'] else np.array([])
        
        markers_array = np.array(t2_histogram_data['markers'], dtype=[
            ('record_num', 'i4'), ('time_tag', 'i8'), ('markers', 'u1')
        ]) if t2_histogram_data['markers'] else np.array([])
        
        overflows_array = np.array(t2_histogram_data['overflows'], dtype=[
            ('record_num', 'i4'), ('count', 'u2')
        ]) if t2_histogram_data['overflows'] else np.array([])
        
        result_dict = {
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
            'photon_times': t2_histogram_data['photon_times'],
            'T2channel': t2_histogram_data['channel'],
            'statistics': {
                'photons': t2_histogram_data['photon_count'],
                'markers': t2_histogram_data['marker_count'],
                'overflows': t2_histogram_data['overflow_count']
            },
            # T2 Time-Correlation Single Photon Counting
            'tcspc': {
                'photon_times': t2_histogram_data['photon_times'],
                'histogram': t2_histogram_data['histogram'],
                'time_axis': t2_histogram_data['time_axis'],
                'histogrammed_photons': t2_histogram_data['histogrammed_photons'],
                'sync_times': t2_histogram_data['sync_times'],
                'signal_times': t2_histogram_data['signal_times'],
                'parameters': {
                    'sync_channel': t2_histogram_data['sync_channel'],
                    'signal_channel': t2_histogram_data['signal_channel'],
                    'time_window_ns': t2_histogram_data['time_window_ns'],
                    'bin_width_ps': t2_histogram_data['bin_width_ps'],
                    'n_bins': t2_histogram_data['n_bins']
                },
                'statistics': {
                    'sync_rate_MHz': t2_histogram_data['sync_rate_MHz'],
                    'photon_rate_MHz': t2_histogram_data['photon_rate_MHz'],
                    'counts_per_sync': t2_histogram_data['counts_per_sync'],
                    'n_sync_pulses': t2_histogram_data['n_sync_pulses'],
                    'n_signal_photons': t2_histogram_data['n_signal_photons'],
                }
            }
        }
    
    return result_dict

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

    # Check timing - last true time should be close to the actual experiment duration
    """if photon_times:
        first_time = photon_times[0][1]
        last_time = photon_times[-1][1]
        print(f"\nFirst photon: {first_time/1e9:.3f} s")
        print(f"Last photon: {last_time/1e9:.3f} s")
        print(f"Duration: {(last_time - first_time)/1e9:.3f} s")"""

def readT2(file, sync_channel=0, signal_channel=1, time_window_ns=50, bin_width_ps=25):
    """
    Read PicoHarp T2 format data and reconstruct T3-style histogram.
    
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

    # Initialize all variables
    ofltime = 0
    WRAPAROUND = 210698240
    record_num = 0
    
    # Original data structures
    photons = []
    markers = []
    overflows = []
    photon_count = 0
    overflow_count = 0
    marker_count = 0
    photon_times = []
    channel = []
    
    # For T3 reconstruction (sync times and photon times separately)
    sync_times = []           # Absolute times of all sync pulses (ns)
    signal_times = []         # Absolute times of all signal photons (ns)
    
    # For histogramming - use separate arrays for processing
    all_sync_times = []
    all_signal_times = []
    
    # Histogram parameters 
    bin_width_ns = bin_width_ps / 1000  # Convert ps to ns
    n_bins = int(time_window_ns / bin_width_ns)
    histogram = np.zeros(n_bins, dtype=np.int64)
    histogrammed_photons = 0
    sync_to_photon_times = []  # Store individual delay times for debugging
    
    # =============================================================
    # FIRST PASS: Read all data and collect sync/signal times
    # =============================================================
    for i in range(TTResult_NumberOfRecords):
        # Read 32-bit record
        t2_record = struct.unpack('I', file.read(4))[0]
        
        # Extract components
        t2time = t2_record & 0xFFFFFFF        # Lower 28 bits: time tag
        chan = (t2_record >> 28) & 0xF        # Upper 4 bits: channel
        
        # Apply overflow correction to get absolute time tag
        timetag = ofltime + t2time
        
        # Store original data structures
        if 0 <= chan <= 4:
            # Convert to absolute time in nanoseconds
            true_time_ns = timetag * MeasDesc_GlobalResolution * 1e9
            
            # Store in original structures
            photon_times.append(true_time_ns)
            channel.append(chan)
            photons.append((
                record_num,     # Record number in file
                timetag,        # Absolute time tag value
                chan,           # Channel (0-4)
                0,              # Dtime is 0 for T2 mode (not applicable)
                true_time_ns    # Absolute time in nanoseconds
            ))
            photon_count += 1
            
            # Collect sync and signal times
            if chan == sync_channel:
                all_sync_times.append(true_time_ns)
            elif chan == signal_channel:
                all_signal_times.append(true_time_ns)
                
        elif chan == 15:
            # =============================================================
            # SPECIAL RECORD: Either overflow or marker
            # =============================================================
            markers_val = t2_record & 0xF  # Marker bits (lowest 4 bits)
            
            if markers_val == 0:
                # =========================================================
                # OVERFLOW RECORD: Time tag counter wrapped around
                # =========================================================
                ofltime += WRAPAROUND
                overflows.append((record_num, 1))
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
    
    # =============================================================
    # SECOND PASS: Reconstruct T3 histogram
    # For each photon, find the PREVIOUS sync pulse
    # =============================================================
    sync_idx = 0  # Index for sync pulses
    n_syncs = len(all_sync_times)
    
    for photon_time in all_signal_times:
        # Find the sync pulse that occurred immediately before this photon
        # Since both arrays are sorted (time-ordered), we can advance sync_idx
        while sync_idx < n_syncs and all_sync_times[sync_idx] < photon_time:
            sync_idx += 1
        
        # The previous sync pulse is at sync_idx - 1
        if sync_idx > 0:  # Found a preceding sync pulse
            prev_sync_time = all_sync_times[sync_idx - 1]
            time_since_sync = photon_time - prev_sync_time
            
            # Store for debugging/analysis
            sync_to_photon_times.append(time_since_sync)
            sync_times.append(prev_sync_time)
            signal_times.append(photon_time)
            
            # Check if within histogram window (positive and bounded)
            if 0 <= time_since_sync < time_window_ns:
                bin_idx = int(time_since_sync / bin_width_ns)
                if 0 <= bin_idx < n_bins:
                    histogram[bin_idx] += 1
                    histogrammed_photons += 1
    
    # Create time axis for the histogram
    time_axis = np.arange(n_bins) * bin_width_ns + bin_width_ns/2  # Center of bins
    
    # Calculate statistics
    total_time_ns = 0
    if len(sync_times) > 0:
        total_time_ns = max(max(sync_times), max(all_signal_times)) if all_signal_times else max(sync_times)
    
    sync_rate = (len(all_sync_times) / total_time_ns * 1e9) if total_time_ns > 0 else 0
    photon_rate = (len(all_signal_times) / total_time_ns * 1e9) if total_time_ns > 0 else 0
    counts_per_sync = len(all_signal_times) / len(all_sync_times) if len(all_sync_times) > 0 else 0

    # Return complete dataset
    return {
        # Original data 
        'photons': photons,
        'markers': markers,
        'overflows': overflows,
        'photon_times': photon_times,
        'channel': channel,
        'photon_count': photon_count,
        'overflow_count': overflow_count,
        'marker_count': marker_count,
        
        # T3-reconstructed data
        'sync_times': sync_times,
        'signal_times': signal_times,
        'sync_to_photon_times': sync_to_photon_times,
        
        # Histogram data (now matches T3 mode)
        'histogram': histogram,
        'time_axis': time_axis,
        'histogrammed_photons': histogrammed_photons,
        'total_histogram_counts': histogram.sum(),
        
        # Raw data for reference
        'raw_sync_times': all_sync_times,
        'raw_signal_times': all_signal_times,
        
        # Parameters
        'sync_channel': sync_channel,
        'signal_channel': signal_channel,
        'time_window_ns': time_window_ns,
        'bin_width_ps': bin_width_ps,
        'n_bins': n_bins,
        
        # Statistics
        'sync_rate_MHz': sync_rate,
        'photon_rate_MHz': photon_rate,
        'counts_per_sync': counts_per_sync,
        'total_time_ns': total_time_ns,
        'n_sync_pulses': len(all_sync_times),
        'n_signal_photons': len(all_signal_times),
        'n_histogrammed_photons': histogrammed_photons,
    }

"""def readT2(file, sync_channel=0, signal_channel=1, time_window_ns=50, bin_width_ps=25):
    
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
    

    # Initialize all variables
    ofltime = 0
    WRAPAROUND = 210698240
    record_num = 0
    
    # Original data structures
    photons = []
    markers = []
    overflows = []
    photon_count = 0
    overflow_count = 0
    marker_count = 0
    photon_times = []
    channel = []
    
    # For histogramming
    sync_times = []           # Absolute times of all sync pulses (ns)
    signal_times = []         # Absolute times of all signal photons (ns)
    last_sync_time_ns = None  # Most recent sync time for histogramming
    
    # Histogram parameters 
    bin_width_ns = bin_width_ps / 1000  # Convert ps to ns (CHECK THIS!)
    n_bins = int(time_window_ns / bin_width_ns)
    histogram = np.zeros(n_bins, dtype=np.int64)
    histogrammed_photons = 0
    sync_to_photon_times = []  # Store individual delay times for debugging
    
    # Process each record in a single pass
    for i in range(TTResult_NumberOfRecords):
        # Read 32-bit record
        t2_record = struct.unpack('I', file.read(4))[0]
        
        # Extract components
        t2time = t2_record & 0xFFFFFFF        # Lower 28 bits: time tag
        chan = (t2_record >> 28) & 0xF        # Upper 4 bits: channel
        
        # Apply overflow correction to get absolute time tag
        timetag = ofltime + t2time
        
        # Store original data structures (your existing code)
        if 0 <= chan <= 4:
            # Convert to absolute time in nanoseconds
            true_time_ns = timetag * MeasDesc_GlobalResolution * 1e9
            
            # Store in original structures
            photon_times.append(true_time_ns)
            channel.append(chan)
            photons.append((
                record_num,     # Record number in file
                timetag,        # Absolute time tag value
                chan,           # Channel (0-4)
                0,              # Dtime is 0 for T2 mode (not applicable)
                true_time_ns    # Absolute time in nanoseconds
            ))
            photon_count += 1
            
            # =============================================================
            # SINGLE-PASS HISTOGRAMMING
            # =============================================================
            if chan == sync_channel:
                # Store sync time and update most recent sync
                sync_times.append(true_time_ns)
                last_sync_time_ns = true_time_ns
                
            elif chan == signal_channel:
                # Store signal photon time
                signal_times.append(true_time_ns)
                
                # If we have a sync pulse reference, histogram this photon
                if last_sync_time_ns is not None:
                    # Calculate time since last sync pulse
                    time_since_sync = true_time_ns - last_sync_time_ns
                    
                    # Store for debugging/analysis
                    sync_to_photon_times.append(time_since_sync)
                    
                    # Check if within histogram window (positive and bounded)
                    if 0 <= time_since_sync < time_window_ns:
                        bin_idx = int(time_since_sync / bin_width_ns)
                        if bin_idx < n_bins:
                            histogram[bin_idx] += 1
                            histogrammed_photons += 1
                
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
    
    # Create time axis for the histogram
    time_axis = np.arange(n_bins) * bin_width_ns + bin_width_ns/2  # Center of bins
    
    # Calculate statistics
    total_time_ns = 0
    if len(sync_times) > 0 and len(signal_times) > 0:
        total_time_ns = max(sync_times[-1], signal_times[-1]) if signal_times else sync_times[-1]
    
    sync_rate = (len(sync_times) / total_time_ns * 1e9) if total_time_ns > 0 else 0
    photon_rate = (len(signal_times) / total_time_ns * 1e9) if total_time_ns > 0 else 0
    counts_per_sync = len(signal_times) / len(sync_times) if len(sync_times) > 0 else 0

    # Return complete dataset
    return {
        # Original data 
        'photons': photons,
        'markers': markers,
        'overflows': overflows,
        'photon_times': photon_times,
        'channel': channel,
        'photon_count': photon_count,
        'overflow_count': overflow_count,
        'marker_count': marker_count,
        
        # New data for histogramming
        'sync_times': sync_times,
        'signal_times': signal_times,
        'sync_to_photon_times': sync_to_photon_times,
        
        # Histogram data
        'histogram': histogram,
        'time_axis': time_axis,
        'histogrammed_photons': histogrammed_photons,
        'total_histogram_counts': histogram.sum(),
        
        # Parameters
        'sync_channel': sync_channel,
        'signal_channel': signal_channel,
        'time_window_ns': time_window_ns,
        'bin_width_ps': bin_width_ps,
        'n_bins': n_bins,
        
        # Statistics
        'sync_rate_MHz': sync_rate,
        'photon_rate_MHz': photon_rate,
        'counts_per_sync': counts_per_sync,
        'total_time_ns': total_time_ns,
        'n_sync_pulses': len(sync_times),
        'n_signal_photons': len(signal_times),
    }"""

def readDAT(file):
    """
    Read .dat file format where:
    - First 10 lines are header information
    - Remaining lines are photon counts
    
    Args:
        filepath: Path to the .dat file
        
    Returns:
        Dictionary with similar structure to PTU data for consistency
    """

    print("="*60)
    print("HEADER INFORMATION")
    print("="*60)

    Header_Data = {}

    with open(file, "r") as file:
        # Read and parse the header lines
        first_line = file.readline().split()
        if len(first_line) >= 7:
            Header_Data['HW_Type'] = f"{first_line[0]} {first_line[1]}"
            Header_Data['File_CreatingDate'] = first_line[4]
            Header_Data['File_CreatingTime'] = f"{first_line[5]} {first_line[6]}"
        
        # Skip empty line
        file.readline()
        
        # Read channels per curve
        channels_line = file.readline().strip()
        Header_Data['Channels_Per_Curve'] = int(channels_line) if channels_line.isdigit() else channels_line
        
        # Skip empty line  
        file.readline()
        
        # Read display curve number
        display_curve_line = file.readline().strip()
        Header_Data['Display_Curve_no'] = int(display_curve_line) if display_curve_line.isdigit() else display_curve_line
        
        # Skip empty line
        file.readline()
        
        # Read memory block number
        memory_block_line = file.readline().strip()
        Header_Data['Memory_Block_no'] = int(memory_block_line) if memory_block_line.isdigit() else memory_block_line
        
        # Skip empty line
        file.readline()
        
        # Read NS per channel
        ns_channel_line = file.readline().strip()
        Header_Data['NS_Per_Channel'] = float(ns_channel_line) if ns_channel_line.replace('.', '').isdigit() else ns_channel_line
        
        # Additional header fields to match PTU format
        Header_Data['File_Comment'] = 'DAT File Converted'
        Header_Data['Measurement_Mode'] = 'Histogramming mode'
        Header_Data['TTResultFormat_TTTRRecType'] = 'DAT_FILE'
        Header_Data['TTResultFormat_BitsPerRecord'] = 32
        Header_Data['MeasDesc_Resolution'] = Header_Data.get('NS_Per_Channel', 1.0)
        Header_Data['MeasDesc_GlobalResolution'] = Header_Data.get('NS_Per_Channel', 1.0)
        Header_Data['MeasDesc_AcquisitionTime'] = 0  
        Header_Data['TTResult_NumberOfRecords'] = 0  

        # Print header information
        for key, value in Header_Data.items():
            if isinstance(value, str):
                print(f"{key:<35} '{value}'")
            elif isinstance(value, (int, float)):
                print(f"{key:<35} {value}")
            else:
                print(f"{key:<35} {value}")
        print("="*60)

        isT2 = 0
        photon_times = np.loadtxt(file, unpack=True, skiprows=10)
        photon_times = np.trim_zeros(photon_times)
        
        # Since this is .dat file and in T2 mode these values are not recorded in this format
        photon_count = 'N/A'
        marker_count = 'N/A'
        overflow_count = 'N/A'
        photons_array = []
        markers_array = []
        overflows_array = []

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