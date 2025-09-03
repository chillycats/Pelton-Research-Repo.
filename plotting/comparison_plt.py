#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
comparison_plot

The comparison_plot function aims to plot all of the fits the user determined with the normalized main data all on one graph so
that the user can compare each fit against one another. It first determines whether or not there are two or three fits to 
compare then assigns the proper label for each fit. After it assigns all the correct labels it will plot each of the fits. If 
there is only one fit then the function will not plot anything and will return.

Args:   
    measurement_type: the number corresponding to the type of measurement; this will be needed for determining the correct titles for the plot
    num_of_fits: the number of fits the program will plot for comparison
    time_array: time_array
    main_data: normalized main data
    fit1: fitted data for the first fit
    num_exp_fit1: number of terms in the first fit
    fit2: fitted data for the second fit
    num_exp_fit2: number of terms in the second fit
    fit3: fitted data for the third fit
    num_exp_fit3: number of terms in the third fit

Returns:
    N/A
"""


def comparison_plot(measurement_type, num_of_fits, time_array, main_data, num_exp_fit1, fit1, num_exp_fit2, fit2, num_exp_fit3, fit3):
    # determing the correct labels for the y-axis and title depending on the measurement made
    if measurement_type == 1:
        ylabel = 'Normalized PL (a.u.)'
        title = 'Comparison of Fits for Flourescence Decay Data'
    elif measurement_type == 2:
        ylabel = '$g^{(2)}(\\tau)$'
        title = 'Comparison of Fits for g2 Pulsed Data'
    else:
        ylabel = 'Coincidence Counts'
        title = 'Comparison of Fits for g2 CW Autocorrelation Data'


    # for two fits
    if num_of_fits == 2:
        # using a for loop to determine the correct labels for each fit
        kind_of_fit = [num_exp_fit1, num_exp_fit2]
        for n in range(len(kind_of_fit)):
            if kind_of_fit[n] == 1:
                kind_of_fit[n] = 'Exponential Fit'
            elif kind_of_fit[n] == 2:
                kind_of_fit[n] = 'Bi-Exponential Fit'
            else:
                kind_of_fit[n] = 'Tri-Exponential Fit'

        fit1_label = kind_of_fit[0]
        fit2_label = kind_of_fit[1]

        # plotting the comparison plot
        fig4, comparison_plot = plt.subplots(figsize = (12,6))

        comparison_plot.plot(time_array, main_data, color = 'black', label = 'Normalized Data')
        comparison_plot.plot(time_array, fit1, color = 'blue', linestyle = '--', label = f"{fit1_label}")
        comparison_plot.plot(time_array, fit2, color = 'green', linestyle = '--', label = f"{fit2_label}")
        comparison_plot.set_yscale("log")
        comparison_plot.legend()
        comparison_plot.set_xlabel("Delay Time (ns)")
        comparison_plot.set_ylabel(f"{ylabel}")
        comparison_plot.set_title(f"{title}")

    # for three fits
    elif num_of_fits == 3:
        # using a for loop to determine the correct labels for each fit
        kind_of_fit = [num_exp_fit1, num_exp_fit2, num_exp_fit3]
        for n in range(len(kind_of_fit)):
            if kind_of_fit[n] == 1:
                kind_of_fit[n] = 'Exponential Fit'
            elif kind_of_fit[n] == 2:
                kind_of_fit[n] = 'Bi-Exponential Fit'
            else:
                kind_of_fit[n] = 'Tri-Exponential Fit'

        fit1_label = kind_of_fit[0]
        fit2_label = kind_of_fit[1] 
        fit3_label = kind_of_fit[2]  

        # plotting the comparison plot
        fig, comparison_plot = plt.subplots(figsize = (12,6))

        comparison_plot.plot(time_array, main_data, color = 'black', label = 'Normalized Main Data')
        comparison_plot.plot(time_array, fit1, color = 'blue', linestyle = '--', label = f"{fit1_label}")
        comparison_plot.plot(time_array, fit2, color = 'green', linestyle = '--', label = f"{fit2_label}")
        comparison_plot.plot(time_array, fit3, color = 'red', linestyle = '--', label = f"{fit3_label}")
        comparison_plot.set_yscale("log")
        comparison_plot.legend()
        comparison_plot.set_xlabel("Delay Time (ns)")
        comparison_plot.set_ylabel(f"{ylabel}")
        comparison_plot.set_title(f"{title}")

    # special case where there is only one fit
    else:
        return