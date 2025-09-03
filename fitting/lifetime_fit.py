#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
safe_exp

value = the value of the exponential of a varying time and constant tau value

Since we are using exponential decay functions we know that at certain values close to zero they approach zero. This function simply trims values that
are near that region so that the fits don't obstruct our ability to see the decay of the data that we are interested in.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

lifetime_exponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term

This function returns the fit function corresponding to the one term exponential fit. It does so by returning a function that does call the safe_exp
function to avoid the problem mentioned in the safe_exp description.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

lifetime_biexponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term
A2 = constant in front of the second exponential term
tau2 = time constant for the second exponential term

This function returns the fit function corresponding to the two term exponential fit. It does so by returning a function that does call the safe_exp
function to avoid the problem mentioned in the safe_exp description.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

lifetime_triexponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term
A2 = constant in front of the second exponential term
tau2 = time constant for the second exponential term
A3 = constant in front of the third exponential term
tau3 = time constant for the third exponential term

This function returns the fit function corresponding to the three term exponential fit. It does so by returning a function that does call the safe_exp
function to avoid the problem mentioned in the safe_exp description.
"""

# Define Safe Exponential Function to Avoid Overflow
def safe_exp(value):
    return np.exp(np.clip(value, -700, 0))

# Define Exponential Model
def lifetime_exponential(t, A1, tau1):
    return A1 * safe_exp(-t/tau1)

# Define Biexponential Model
def lifetime_biexponential(t, A1, tau1, A2, tau2):
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2)

# Define Triexponential Model
def lifetime_triexponential(t, A1, tau1, A2, tau2, A3, tau3):
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2) + A3 * safe_exp(-t / tau3)

"""
data_analysis

num_of_exponentials = the number of terms in the fit
data = normalized data array that
time = time array
guesses = a list of integers corresponding to the constants and time constants in the form [A1, tau1, A2, tau2, A3, tau3]

The data_analysis function returns a fit of the data from a given exponential fit  and the corresponding residuals that is inputted by the user. It does so by first determining how
many exponential terms are in the fit then executing the following process:
    1. Trim any zeros from the guesses list so that we do not encounter any divide by zeros errors (this is dependent on how many exponential terms there
    are)
    2. Then it will execute a curve_fit which calls a function to define the fit being used (exponential, biexponential, triexponential functions) which
    return the corresponding function for the fit
    3. Then it defines the actual constants (A1, tau1, A2, tau2, A3, tau3) and their errors (which is found from the diagonals of the pcov_exp matrix)
    4. Then it normalizes the fit
    5. Makes a list of the actual constants and their errors
    6. Determines the residuals
    7. Makes a 2D array of the actual constants, normalized fit, and residuals
    8. Returns the above 2D array
"""

def T2_lifetime_data_analysis(num_of_exponentials, data, time, guesses):
    if num_of_exponentials == 1: # one term exponential fit
        guesses = np.trim_zeros(guesses) #reduces guesses list to constants important to the fit
        popt_exp, pcov_exp = curve_fit(lifetime_exponential, time, data, p0=guesses, maxfev=2000) #fitting the data to the model
        A1_exp, tau1_exp = popt_exp #defining the "new.updated" constants
        errors_exp = np.sqrt(np.diag(pcov_exp)) #determining the errors from the diagonal of the matrix
        fit_exp_normalized = lifetime_exponential(time, *popt_exp) / np.max(data) #normalizing the fit
        parameters = [A1_exp, tau1_exp, errors_exp] #list of the parameter information
        residual1 = data - fit_exp_normalized #determining the residuals

        exp_fit_model = [num_of_exponentials, parameters, fit_exp_normalized, residual1] #2D list of the parameter information and the normalized fit
        return exp_fit_model

    elif num_of_exponentials == 2: # two term exponential fit
        guesses = np.trim_zeros(guesses) #reduces guesses list to constants important to the fit
        popt_bi, pcov_bi = curve_fit(lifetime_biexponential, time, data, p0=guesses, maxfev=2000) #fitting the data to the model
        A1_bi, tau1_bi, A2_bi, tau2_bi = popt_bi #defining the "new/updated" constants
        errors_bi = np.sqrt(np.diag(pcov_bi)) #determining the errors from the diagonal of the matrix
        fit_bi_normalized = lifetime_biexponential(time, *popt_bi) / np.max(data) #normalizing the fit
        parameters = [A1_bi, tau1_bi, A2_bi, tau2_bi, errors_bi] #list of the parameter information
        residual2 = data - fit_bi_normalized #determining the residuals

        bi_fit_model = [num_of_exponentials, parameters, fit_bi_normalized, residual2] #2D list of the parameter information and the normalized fit
        return bi_fit_model

    else: # three term exponential fit
        popt_tri, pcov_tri = curve_fit(lifetime_triexponential, time, data, p0=guesses, maxfev=5000) #fitting the data to the model
        A1_tri, tau1_tri, A2_tri, tau2_tri, A3_tri, tau3_tri = popt_tri #defining the "new/updated" constants
        errors_tri = np.sqrt(np.diag(pcov_tri)) #determining the errors from the diagonal of the matrix
        fit_tri_normalized = lifetime_triexponential(time, *popt_tri) / np.max(data) #normalizing the fit
        parameters = [A1_tri, tau1_tri, A2_tri, tau2_tri, A3_tri, tau3_tri, errors_tri] #list of the parameter information
        residual3 = data - fit_tri_normalized #determining the residuals

        tri_fit_model = [num_of_exponentials, parameters, fit_tri_normalized, residual3] #2D list of the parameter information and the normalized fit
        return tri_fit_model