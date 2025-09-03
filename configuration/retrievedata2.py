#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
retrieve_data

This functio works by taking a user input and using the given directory to find the filename and load the
data. The function will return an array of the data points.

Args:
    path: the file path provided by the user

Returns:
    numpy.ndarray of the data
"""

def retrieve_data(path):
    # file contains two important constants and the histogram data points
    # skip the first rows as they are part of the header
    file = np.loadtxt(path, unpack=True, skiprows = 10)

    # removing the 'data' that was collected after the experiment ended
    data = np.trim_zeros(file)

    return data