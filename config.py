# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  
#                         Configuration Parameters for DQE
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

"""
 - - - - - - - - - - - - - - - - - 
        Measurement Type
 - - - - - - - - - - - - - - - - - 
 0 = None of the measurement types listed below will consequentially only plot the 'raw' data
 1 = Lifetime Measurement
 2 = g2 CW Autocorrelations
 3 = g2 Pulsed
 - - - - - - - - - - - - - - - - - 
 """

MeasurementType = 1

# Background/Measurement File Information
Bfilepath = ''
# Please enter this value in seconds - if no file leave the placeholder '1' value
Bduration = 1
Mduration = 1

# Bin size for histogramming - put in picoseconds
bin_width_ps = 25
# Time window for histogramming - put in nanoseconds
time_window_ns = 50

# Trimming Parameter - determines how much of the data DQE should truncate
# Generally 1500 is good for lifetime and g2 autocorrelations measurements and
# 15000 is good for g2 pulsed measurements
trimming_threshold = 1500

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                               Fitting Parameters
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Lifetime Fit Parameters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Each fit array are in the form:
#
# [A1, Tau1, A2, Tau2, A3, Tau3]
#
# where A is the constant in front of an exponential term and tau is the time constant.
# DQE is only meant to work with fits that go up to three exponential terms. If you choose
# to plot one or two fits DQE will plot fit1 or fit1 and fit2 respectively. 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -

LNumFits = 1

Lfit1 = [500, 100, 50, 10, 20, 5]
Lfit2 = [500, 100, 50, 10, 0, 0]
Lfit3 = [500, 100, 0, 0, 0, 0]

Generic_Lifetime = r"$A_1 e^{-t/\tau_1} + A_2 e^{-t/\tau_2} + A_3 e^{-t/\tau_3}$"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# g2 specific variables
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# If the measurement file is in a .dat file you will need to manually define the
#  following variables:

sync_rate = 1
input_rate = 1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# g2 CW Autocorrelation Fit Parameters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -

CW_Zero_Time_Offset = 55 # in nanoseconds
CFit1 = [0.5, 5]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# g2 Pulsed Fit Parameters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Each fit array are in the form:
# [A1, Tau1, A2, Tau2, R]
#
# where A is the constant in front of each exponential term and tau is the time constant.
# R is a constant that is multiplied by each exponential. The program is designed to only 
# work with fits that go up to two exponential terms. If you choose to plot one or two fits 
# the program will plot fit1 or fit1 and fit2 respectively.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -

Pulse_Period_ns = 410 # in nanoseconds
Pulsed_Zero_Time_Offset = 68 # in nanoseconds
Pfit1 = [0.5, 5, 0.5, 20, 0.5]

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                          Blinking & Bleaching Parameters
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

"""
 - - - - - - - - - - - - - - - - - 
           00_Blinking 
 - - - - - - - - - - - - - - - - - 
 0 = The program will NOT apply the blinking code to the data file
 1 = The program will apply the blinking code to the data file
 - - - - - - - - - - - - - - - - - 
 """
OO_Blinking = 1

# On/Off threshold - represented as a fraction of the peak intensity
OO_Threshold = 0.2 
# Bin size for blinking
blink_bin_width = 0.08