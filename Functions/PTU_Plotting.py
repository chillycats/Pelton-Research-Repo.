#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

from Functions.plotting_config import LExp, LBiExp, LTriExp

""""
plots

num_of_termss = the number of terms for the inputted fit
time_array = time array
main_data = normalized main data array
fitted_data = fitted data for a given fit determined by the user
residuals = subtraction of the main data and fitted data

The plots function aims to plot each fit and its respective residuals for the normalized main data set without returning anything. Based on the number of 
exponentials in the fit the program will change the name and color of the plot of the fitted data. Meanwhile, the normalized main data will always be 
assigned the color black along with the respective residuals. 
"""

def plots(model, time_array, main_data, fitted_data, residuals):
    PlotInfo = {}
    # Lifetime Models
    if model == 'Exponential Fit':
        PlotInfo = LExp
    elif model == 'Bi-Exponential Fit':
        PlotInfo = LBiExp
    elif model == 'Tri-Exponential Fit':
        PlotInfo = LTriExp

    # Plotting - upper is the fitted data and main data vs. time, lower - residuals plot
    gs_kw = dict(height_ratios=[2,1]) # determines the height ratio s.t. the residuals are below and smaller than the upper plot
    fig, axd = plt.subplot_mosaic([['upper'],
                               ['lower']],
                              gridspec_kw=gs_kw, figsize=(12, 6),
                              layout="constrained")
    # plotting the upper plot
    axd['upper'].plot(time_array, main_data, color = 'black', label = 'Normalized Data')
    axd['upper'].plot(time_array, fitted_data, color = f"{PlotInfo['FColor']}", linestyle = '--', label = f"{PlotInfo['FLabel']}")
    axd['upper'].legend()
    axd['upper'].set_yscale("log")
    axd['upper'].set_xlabel("Delay Time (ns)")
    axd['upper'].set_ylabel("Normalized PL (a.u.)")
    axd['upper'].set_title(f"{PlotInfo['Subtitle']}")

    # plotting the lower plot
    axd['lower'].plot(time_array, residuals, color = 'black')
    axd['lower'].set_xlabel("Delay Time (ns)")
    axd['lower'].set_ylabel("Residuals")
    axd['lower'].set_title("Residuals Plot of Flourescence Decay Data")

    # name of the overall figure
    fig.suptitle(f"{PlotInfo['MTitle']}")

    return fig

"""
comparison_plot

num_of_fits = the number of fits the program will plot for comparison
time_array = time_array
main_data = normalized main data
fit1 = fitted data for the first fit
num_exp_fit1 = number of terms in the first fit
fit2 = fitted data for the second fit
num_exp_fit2 = number of terms in the second fit
fit3 = fitted data for the third fit
num_exp_fit3 = number of terms in the third fit

The comparison_plot function aims to plot all of the fits the user determined with the normalized main data all on one graph so that the user can compare
each fit against one another. It first determines whether or not there are two or three fits to compare then assigns the proper label for each fit. After
it assigns all the correct labels it will plot each of the fits. If there is only one fit then the function will not plot anything and will return.
"""


def comparison_plot(num_of_fits, time_array, main_data, model1, fit1, model2, fit2, model3, fit3):

    PlotInfos = []

    fits = [fit1, fit2, fit3]
    models = [model1, model2, model3]
    models = np.trim_zeros(models)

    for i in range(num_of_fits):
        # Lifetime Models
        if models[i] == 'Exponential Fit':
            PlotInfos.append(LExp)
        elif models[i] == 'Bi-Exponential Fit':
            PlotInfos.append(LBiExp)
        elif models[i] == 'Tri-Exponential Fit':
            PlotInfos.append(LTriExp)
    
     # plotting the comparison plot
    fig4, comparison_plot = plt.subplots(figsize = (12,6))

    comparison_plot.plot(time_array, main_data, color = 'black', label = 'Normalized Data')
    for i in range(len(fits)):
        comparison_plot.plot(time_array, fits[i], color = f"{PlotInfos[i]['FColor']}", linestyle = '--', label = f"{PlotInfos[i]['FLabel']}")
    comparison_plot.set_yscale("log")
    comparison_plot.legend()
    comparison_plot.set_xlabel("Delay Time (ns)")
    comparison_plot.set_ylabel("Normalized PL (a.u.)")
    comparison_plot.set_title("Comparison of Fits for Flourescence Decay Data")

    return fig4