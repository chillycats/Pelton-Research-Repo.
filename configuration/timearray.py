#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
time_array_construction

This function works by constructing the time array for a respective measurement type.  

Args:
    measurement_type: the number corresponding to the corresponding measurement type
    len_data: the length of the trimmed normalized experimental data
    ns_channel: resolution of the graph
    delay: the delay time between the two detectors (required for g2 measurements)

Returns:
    time_array: np.ndarray of the time axis
"""

def time_array_construction(measurement_type, len_trimmed_data, ns_channel, delay):
    # for lifetime measurements
    if measurement_type == 1:
        # defining the time array
        time_array = np.arange(0, len_trimmed_data * ns_channel, ns_channel)
        return time_array
    # for g2 pulsed measurements
    elif measurement_type == 2:
        # defining the time array
        time_array = []
        print("Time array function is not avaliable at this time.")
        return 
    # for g2 CW autocorrelation measurements
    elif measurement_type == 3:
        # defining the time array
        time_array = (np.arange(len(len_trimmed_data)) - delay) * ns_channel
        return time_array