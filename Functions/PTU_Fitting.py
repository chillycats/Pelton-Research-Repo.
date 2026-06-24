#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy import signal
import os

# Define Safe Exponential Function to Avoid Overflow
def safe_exp(value):
    """
    Safe Exponential Function

    value = the value of the exponential of a varying time and constant tau value

    Since we are using exponential decay functions we know that at certain values close to zero they 
    approach zero. This function simply trims values that are near that region so that the fits don't 
    obstruct our ability to see the decay of the data that we are interested in.
    """
    return np.exp(np.clip(value, -700, 0))

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                   LIFETIME MODELS & FITTING
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# = = = = = = = = = = = = = = = = = = = = = = =
#                   MODELS
# = = = = = = = = = = = = = = = = = = = = = = =

# Define Exponential Model
def exponential(t, A1, tau1):
    """
    Exponential Fit

    A_n = Constants in front of exponential term(s)
    Tau_n = Time constants for exponential term(s)
    """
    return A1 * safe_exp(-t/tau1)

# Define Biexponential Model
def biexponential(t, A1, tau1, A2, tau2):
    """
    Bi-Exponential Fit

    A_n = Constants in front of exponential term(s)
    Tau_n = Time constants for exponential term(s)
    """
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2)

# Define Triexponential Model
def triexponential(t, A1, tau1, A2, tau2, A3, tau3):
    """
    Tri-Exponential Fit

    A_n = Constants in front of exponential term(s)
    Tau_n = Time constants for exponential term(s)
    """
    return A1 * safe_exp(-t / tau1) + A2 * safe_exp(-t / tau2) + A3 * safe_exp(-t / tau3)

# = = = = = = = = = = = = = = = = = = = = = = =
#                   FITTING
# = = = = = = = = = = = = = = = = = = = = = = =
    
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

    # Normalizing fit, calculating residuals, and calculating errors
    Nfit = fit(time,*popt) / np.max(data)
    Residuals = data - Nfit
    Errors = np.sqrt(np.diag(pcov))

    print("="*60)
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

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#             g2 CW AUTICORRELATION MODELS & FITTING
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# = = = = = = = = = = = = = = = = = = = = = = =
#                   MODELS
# = = = = = = = = = = = = = = = = = = = = = = =

def g2_CW_Left(t, A,tau, t0):
    """
    CW Autocorrelation Fit

    t = Time array
    A = Constant in front of the exponential term
    t0 = Offset time (ns)
    tau = Time constant (ns)
    """
    return 40 - (A*np.exp((t-t0)/tau))

def g2_CW_Right(t, A, tau, t0):
    """
    CW Autocorrelation Fit

    t = Time array
    A = Constant in front of the exponential term
    t0 = Offset time (ns)
    tau = Time constant (ns)
    """
    return 40 - (A*np.exp(-(t-t0)/tau))

# = = = = = = = = = = = = = = = = = = = = = = =
#                   FITTING
# = = = = = = = = = = = = = = = = = = = = = = =

def FitCW(data, time, guesses):
    """
    Fit CW Autocorrelation Data

    """

    # Array for printing params
    array = ['A₁', 'τ₁']

    # Smoothing the data to find offset index 
    smooth = signal.savgol_filter(data, 53, 1)
    Offset_Index = np.argmin(smooth)
    t0_guess = time[Offset_Index]

    guesses = [guesses[0], guesses[1], t0_guess]
    
    # Splitting the time to the left and right of the estimated min value
    lmask = time < t0_guess
    rmask = time >= t0_guess

    # Splitting data into the two "halves" for the rise and fall of the fit
    ldata = data[lmask]
    ltime = time[lmask]

    rdata = data[rmask]
    rtime = time[rmask]

    # Fitting the data
    lpopt, lpcov = curve_fit(g2_CW_Left, ltime, ldata, p0=guesses, maxfev=10000)
    rpopt, rpcov = curve_fit(g2_CW_Right, rtime, rdata, p0=guesses, maxfev=10000)

    # Normalizing fit, calculating residuals, and calculating errors 
    lfit = g2_CW_Left(ltime,*lpopt) 
    LResiduals = ldata - lfit
    Errors = np.sqrt(np.diag(lpcov))

    rfit = g2_CW_Right(rtime,*rpopt) 
    RResiduals = rdata - rfit
    Errors = np.sqrt(np.diag(rpcov))

    # Combining everything
    popt = lpopt + rpopt
    fit = np.concatenate((lfit, rfit))
    Residuals = np.concatenate((LResiduals, RResiduals))

    print("="*60)
    print("")

    print("g2 CW Autocorrelation Parameters:")
    print("")
    for i in range(len(array)):
        print(f"\t{array[i]:<15}", end='')
        print(f"{popt[i]} ± {Errors[i]}")

    print("")
    print("="*60)

    fitI = {
        'parameters': popt,
        'errors': Errors,
        'fitted curve': fit,
        'residuals': Residuals, 
        'left data': ldata,
        'right data': rdata,
        'left time': ltime,
        'right time': rtime,
        'left fit': lfit,
        'right fit': rfit,
        'left residuals': LResiduals,
        'right residuals': RResiduals,
    }

    return fitI

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                   g2 PULSED MODELS & FITTING
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# = = = = = = = = = = = = = = = = = = = = = = =
#                   MODELS
# = = = = = = = = = = = = = = = = = = = = = = =
    
def g2_Pulsed(t, pulse_period_ns, y0, A1, tau1, A2, tau2, R, time_offset, num_peaks):
    """
    Fit g2 Pulsed Data

    t = Time array
    A_n = Constant in front of exponential term
    Tau_n = Time constant for each exponential term
    """

    g2_val = y0 + A1 * (R * np.exp(-np.abs((t - time_offset)/tau1)) + 
                       np.sum([np.exp(-np.abs((t - time_offset - n * pulse_period_ns) / tau1)) 
                              for n in range(0, int(num_peaks))], axis=0))
    g2_val += A2 * (R * np.exp(-np.abs((t - time_offset)/tau2)) + 
                   np.sum([np.exp(-np.abs((t - time_offset - n * pulse_period_ns) / tau2)) 
                          for n in range(0, int(num_peaks))], axis=0))
    return g2_val

# = = = = = = = = = = = = = = = = = = = = = = =
#                   FITTING
# = = = = = = = = = = = = = = = = = = = = = = =

def FitPulsed(data, time, guesses, offset, pulse_peaks):

    # Defining the print parameters
    array = ['Pulse Period', 'y0', 'A₁', 'τ₁', 'A₂', 'τ₂', 'R', 'τ0', 'Number of Peaks']

    guesses.append(offset)

    # Smoothing the data to find number of peaks
    smooth = signal.savgol_filter(data, 53, 1)

    # Finding the number of peaks (this doesn't always work and sometimes you will have to 
    # define them yourself)
    peaks, properties = signal.find_peaks(-smooth, prominence=1)
    num_of_peaks = len(peaks)

    # If the user manually defines the number of peaks
    if pulse_peaks != 0:
        num_of_peaks = pulse_peaks

    if len(peaks) >= 2:
        # Calculating the height of the first peak and the average height of remaining peaks
        peak0_height = data[peaks[0]]
        avg_peak_height = np.average(data[peaks[1:]])
        difference = avg_peak_height - peak0_height
    else:
        difference = 'N/A'

    guesses.append(num_of_peaks)

    # Fitting the data
    popt, pcov = curve_fit(g2_Pulsed, time, data, p0=guesses, maxfev=10000)

    # Normalizing fit, calculating residuals, and calculating errors 
    fit = g2_Pulsed(time,*popt) 
    Residuals = data - fit
    Errors = np.sqrt(np.diag(pcov))

    # Finds g2(0) from the fitted function
    g2_zero = g2_Pulsed(0, *popt)
    # Finds fitted pulse period
    g2_Tp = np.max(g2_Pulsed(popt[0], *popt))
    # Normalizes g2(0) where popt[1] = y0_fit
    g2_zero_norm = (g2_zero - popt[1]) / (g2_Tp - popt[1])

    print("="*60)
    print("")

    print("g2 Pulsed Parameters:")
    print("")
    for i in range(len(array)):
        print(f"\t{array[i]:<20}", end='')
        print(f"{popt[i]} ± {Errors[i]}")

    print("")
    print("="*60)

    fitI = {
        'parameters': popt,
        'errors': Errors,
        'fitted curve': fit,
        'residuals': Residuals, 
        'g2(0)': g2_zero_norm,
        'g2 fit period': g2_Tp,
        'height difference': difference
    }

    return fitI