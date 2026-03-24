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

def Ng2(exp_data, bckgrd_data, Mduration, duration_ratio, sync, input, binsize):
    # averages the background data values
    bckgrd_data_avg = np.average(bckgrd_data)

    # multiplies the difference to get the correct average background count for the 
    # duration of experimental measurement duration
    bckgrd_data_avg = bckgrd_data_avg * duration_ratio

    Nsync = sync / Mduration
    Ninput = input / Mduration

    normalized_data = (exp_data / (Nsync * Ninput)) * (Mduration / binsize)

    return normalized_data

