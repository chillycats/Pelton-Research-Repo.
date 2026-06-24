#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
T2_lifetime_normalized

This function works by taking the experimental and background data along with their time durations to determine the normalized 
data set. It does so by first finding the average value from the background and multiplying it by the duration ratio. Then the
program subtracts this value from the experimental data and then normalizes it by dividing by the max value of the experimental
data.

Args:
    exp_data: experimental data array
    bckgrd_data: background data array
    duration_ratio: the ratio of the duration of both experiments (exp_duration / bckgrd_duration)

Returns:
    np.ndarray of the normalized experimental data
"""

def NLifetime(exp_data, bckgrd_data, duration_ratio):
    # averages the background data values
    bckgrd_data_avg = np.average(bckgrd_data)

    # multiplies the difference to get the correct average background count for the 
    # duration of experimental measurement duration
    bckgrd_data_avg = bckgrd_data_avg * duration_ratio

    # finds the index of the maximum value of the experimental data array
    max_index = np.argmax(exp_data) 

    # defines the main data as starting from the max value to the end of the experimental data
    main_data = exp_data[max_index:]
    # subtracts the background from the main data
    main_data_backgrd_subtracted = main_data - bckgrd_data_avg 
    
    # normalizing the main data
    #normalized_data = main_data_backgrd_subtracted / np.max(main_data_backgrd_subtracted)
    normalized_data = main_data / np.max(main_data)

    # returning the normalized main data array
    return normalized_data

def Ng2(exp_data, bckgrd_data, Mduration, duration_ratio, sync_rate, input_rate, binsize):
    # Print all inputs with their values
    print("\n" + "="*60)
    print("INPUT VALUES:")
    print("="*60)
    print(f"Length of exp_data: {len(exp_data)}")
    print(f"exp_data max: {np.max(exp_data)}")
    print(f"bckgrd_data: {bckgrd_data}")
    print(f"Mduration: {Mduration} (type: {type(Mduration)})")
    print(f"duration_ratio: {duration_ratio}")
    print(f"sync_rate: {sync_rate} (type: {type(sync_rate)})")
    print(f"input_rate: {input_rate} (type: {type(input_rate)})")
    print(f"bin_width_ns: {binsize} (type: {type(binsize)})")
    
    # Convert bin width
    bin_width_s = binsize * 1e-9
    print(f"\nbin_width_s: {bin_width_s:.4e} seconds")
    
    # Calculate each term separately
    term1 = sync_rate * input_rate 
    print(f"sync_rate × input_rate = {term1:.4e}")
    
    term2 = term1 * bin_width_s
    print(f"× bin_width_s = {term2:.4e}")
    
    N_accidental = term2 * Mduration
    print(f"× Mduration = {N_accidental:.4e}")
    
    print(f"\nExpected N_accidental (should be ~300): {N_accidental:.4e}")
    
    # Check if Mduration is in the wrong units
    if N_accidental > 1e10:
        print("\n⚠️ WARNING: N_accidental is huge!")
    
    # Test normalization
    test_ratio = np.max(exp_data) / N_accidental
    print(f"\nExpected normalized max: {test_ratio:.4e}")
    print(f"Actual normalized max (should be ~1-2): {test_ratio:.4e}")

    normalized_data = exp_data / N_accidental
    
    """# averages the background data values
    bckgrd_data_avg = np.average(bckgrd_data)

    # multiplies the difference to get the correct average background count for the 
    # duration of experimental measurement duration
    bckgrd_data_avg = bckgrd_data_avg * duration_ratio

    binsize_s = binsize / 1E9

    Nsync = sync_rate * Mduration
    Ninput = input_rate * Mduration

    normalized_data = exp_data / (Nsync * Ninput * binsize_s * Mduration)"""

    print("FINISHED NORMALIZATION")

    return normalized_data

