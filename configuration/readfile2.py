#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
reading_file

This function takes the file name and reads the first few lines of the file to get important information such as the 
date and time of the experiment as well as the ns_channel value and chanels_per_curve value. 

Args:
    path: the file path provided by the user

Returns:
    A list in the following order: [date, time, channels_per_curve, ns_channel]
"""

def reading_file(path):
    file_info = open(path, "r")

    # defining a list that will contain the information of the experiment
    experiment_information = []

    # date of when the data was collected
    date_line = file_info.readline()
    date_of_experiment = date_line.split()[4]
    experiment_information.append(date_of_experiment)
    time_of_experiment = date_line.split()[5]
    experiment_information.append(time_of_experiment)

    print("")

    print("Date and Time of Experiment:", date_of_experiment, time_of_experiment)

    # file contains two important constants and the histogram data points
    file = np.loadtxt(path, unpack=True)

    # defining the important constants
    # length of the data (ie. the number of data points for this experiment; including data collected after experiment)
    channels_per_curve = file[0]
    experiment_information.append(channels_per_curve)
    ns_channel = file[3]
    experiment_information.append(ns_channel)

    print("channels_per_curve =", channels_per_curve)
    print("ns_channel =", ns_channel)

    # returns the list of information of the experiment
    return experiment_information