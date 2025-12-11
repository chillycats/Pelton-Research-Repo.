#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
threshold_trim_function

This function works by taking an approximate derivative using the np.diff function and using the given threshold to determine 
which index the program should trim the data. The aim of this function is to trim the measurement data  when it plateaus around 
a certain value.

Args:
    data: the normalized experimental data
    threshold: the value that identifies the plateau

Returns:
    trimmed_data: a numpy.ndarray of the trimmed normalized experimental data
"""

def threshold_trim_function(normalized_data, threshold):
    # determines the approximate derivative
    derivative_approx = np.diff(normalized_data)

    # sets up two counters to determine when the program should stop the for loop
    # tracks the index
    index_counter = 0
    # tracks how many threshold occurances
    min_threshold_occurances = 0

    # for loop that determines the index the program should trim the normalized data set to
    for i in range(len(derivative_approx)):
        if derivative_approx[i] > 1e5:
            index_counter += 1
        else:
            index_counter += 1
            min_threshold_occurances += 1
            # condition that requires 2500 threshold occurances to stop the loop 
            if min_threshold_occurances >= threshold:
                break

    # creates the np.ndarray of the trimmed normalized data
    trimmed_data = normalized_data[:index_counter]

    # returns np.ndarray of the trimmed normalized experimental data
    return trimmed_data, index_counter