#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
safe_exp

value = the value of the exponential of a varying time and constant tau value

Since we are using exponential decay functions we know that at certain values close to zero they 
approach zero. This function simply trims values that are near that region so that the fits don't 
obstruct our ability to see the decay of the data that we are interested in.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

exponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term

This function returns the fit function corresponding to the one term exponential fit. It does so 
by returning a function that does call the safe_exp function to avoid the problem mentioned in 
the safe_exp description.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

biexponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term
A2 = constant in front of the second exponential term
tau2 = time constant for the second exponential term

This function returns the fit function corresponding to the two term exponential fit. It does so 
by returning a function that does call the safe_exp function to avoid the problem mentioned 
in the safe_exp description.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

triexponential

t = time array
A1 = constant in front of the first exponential term
tau1 = time constant for the first exponential term
A2 = constant in front of the second exponential term
tau2 = time constant for the second exponential term
A3 = constant in front of the third exponential term
tau3 = time constant for the third exponential term

This function returns the fit function corresponding to the three term exponential fit.
It does so by returning a function that does call the safe_exp function to avoid the problem 
mentioned in the safe_exp description.
"""

# Define Safe Exponential Function to Avoid Overflow
def safe_exp(value):
    return np.exp(np.clip(value, -700, 0))

# Define Exponential Model
def exponential(t, A1, tau1):
    return A1 * safe_exp(-t/tau1)

# Define Biexponential Model
def biexponential(t, A1, tau1, A2, tau2):
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2)

# Define Triexponential Model
def triexponential(t, A1, tau1, A2, tau2, A3, tau3):
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2) + A3 * safe_exp(-t / tau3)
    
def FitLifetime(data, time, guesses):
    """
    FitLifetime

    data = normalized data array 
    time = time array
    guesses = a list of integers corresponding to the constants and time constants in the form 
    [A1, tau1, A2, tau2, A3, tau3]

    The FitLifetime function returns a dictonary consisting of the fitted parameters and their 
    errors, the fit itself, and the residuals of the fit.
    """

    guesses = np.trim_zeros(guesses)
    
    # Matches guesses to the correct fit bounds
    bounds = {
        2: [[0, 0.1], [np.inf, np.inf]],                                                # Exp Bounds
        4: [[0, 0.1, 0, 0.1], [np.inf, np.inf, np.inf, np.inf]],                        # BiExp Bounds
        6: [[0, 0.1, 0, 0.1, 0, 0.1], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]] # TriExp Bounds
    }
    
    # Matches guesses to the correct function
    fits = {
        2: exponential,
        4: biexponential,
        6: triexponential
    }

    # Matches guesses to the correct fit name
    model_types = {
        2: 'Exponential Fit',
        4: 'Bi-Exponential Fit',
        6: 'Tri-Exponential Fit'
    }

    # Matches guesses to the correct array format - this is for printing
    arrays = {
        2: ['A₁', 'τ₁'],
        4: ['A₁', 'τ₁', 'A₂', 'τ₂'],
        6: ['A₁', 'τ₁', 'A₂', 'τ₂', 'A₃', 'τ₃']
    }

    # determines the correct fit function to use
    fit = fits.get(len(guesses))
    # if proper fit function doesn't exist raises an error
    if fit == None:
        raise ValueError('ERROR. Please check your Lifetime fitting arrays.')
    
    bound = bounds.get(len(guesses))
    model = model_types.get(len(guesses))
    array = arrays.get(len(guesses))
    
    popt, pcov = curve_fit(fit, time, data, p0=guesses, maxfev=2000, bounds=bound)
    errors = np.sqrt(np.diag(pcov))

    # Normalizing fit, calculating residuals, and calculating errors
    Nfit = fit(time,*popt) / np.max(data)
    Residuals = data - Nfit
    Errors = np.sqrt(np.diag(pcov))

    print("")

    print(f"{model} Parameters:")
    print("")
    for i in range(len(array)):
        print(f"\t{array[i]:<15}", end='')
        print(f"{popt[i]} ± {Errors[i]}")

    print("")
    print("="*60)

    fitI = {
        'model_type': model,
        'parameters': popt,
        'errors': Errors,
        'normalized_fit': Nfit,
        'residuals': Residuals,
    }

    return fitI

    
    
