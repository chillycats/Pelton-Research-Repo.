#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

""""
plots

The plots function aims to plot each fit and its respective residuals for the normalized main data set without returning anything. Based on the number of 
exponentials in the fit the program will change the name and color of the plot of the fitted data. Meanwhile, the normalized main data will always be 
assigned the color black along with the respective residuals. 

Args:
    measurement_type: the number corresponding to the type of measurement
    num_of_terms: the number of terms for the inputted fit
    time_array: time array
    main_data: normalized main data array
    fitted_data: fitted data for a given fit determined by the user
    residuals: subtraction of the main data and fitted data

Returns:
    N/A
"""

def plots(measurement_type, num_of_terms, time_array, main_data, fitted_data, residuals):
    # determing the correct labels for the y-axis and title depending on the measurement made
    if measurement_type == 1:
        ylabel = 'Normalized PL (a.u.)'
        title = 'Flourescence Decay Data'
        master_title = 'and Residuals for Flourescence Decay Data'
        residuals_title = 'Residuals Plot of Flourescence Decay Data'

        # determing the color and respective names for each plot based on the number of terms in each exponential fit
        if num_of_terms == 1:
            fit_color = 'blue'
            fit_label = 'Exponential Fit'
            subtitle = 'Exponential Fit of '
        elif num_of_terms == 2:
            fit_color = 'green'
            fit_label = 'Bi-Exponential Fit' 
            subtitle = 'Bi-Exponential Fit of '
        else:
            fit_color = 'red'
            fit_label = 'Tri-Exponential Fit' 
            subtitle = 'Tri-Exponential Fit of '
    elif measurement_type == 2:
        ylabel = '$g^{(2)}(\\tau)$'
        title = 'g2 Pulsed Data'
        master_title = 'and Residuals for g2 Pulsed Data'
        residuals_title = 'Residuals Plot of g2 Pulsed Data'
    else:
        ylabel = 'Coincidence Counts'
        title = 'g2 CW Autocorrelation Data'
        master_title = 'and Residuals for g2 CW Autocorrelation Data'
        residuals_title = 'Residuals Plot of g2 CW Autocorrelation Data'


    # plotting the two plots - upper is the fitted data and main data vs. time, lower - residuals plot
    gs_kw = dict(height_ratios=[2,1]) # determines the height ratio s.t. the residuals are below and smaller than the upper plot
    fig, axd = plt.subplot_mosaic([['upper'],
                               ['lower']],
                              gridspec_kw=gs_kw, figsize=(12, 6),
                              layout="constrained")
    # plotting the upper plot
    axd['upper'].plot(time_array, main_data, color = 'black', label = 'Normalized Data')
    axd['upper'].plot(time_array, fitted_data, color = f"{fit_color}", linestyle = '--', label = f"{fit_label}")
    axd['upper'].legend()
    axd['upper'].set_yscale("log")
    axd['upper'].set_xlabel("Delay Time (ns)")
    axd['upper'].set_ylabel(f"{ylabel}")
    axd['upper'].set_title(f"{subtitle}" f"{title}")

    # plotting the lower plot
    axd['lower'].plot(time_array, residuals, color = 'black')
    axd['lower'].set_xlabel("Delay Time (ns)")
    axd['lower'].set_ylabel("Residuals")
    axd['lower'].set_title(f"{residuals_title}")

    # name of the overall figure
    fig.suptitle(f"{fit_label}"f"{master_title}" )

    return