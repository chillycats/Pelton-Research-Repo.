# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  
#                         Configuration Parameters for Program
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  
# Paste path to the directory you want to save your files in
# Note that the program will create a folder titled with the today's date (DD-MM-YYYY) and save
# all output files generated on that day to this folder
base_directory = '/Users/jadenchilimigras/Downloads/Research/Pelton/TestingPDFs'

"""
 - - - - - - - - - - - - - - - - - 
        Measurement Type
 - - - - - - - - - - - - - - - - - 
 0 = None of the measurement types listed below will consequentially only plot the raw data
 1 = Lifetime Measurement
 2 = g2 CW Autocorrelations
 3 = g2 Pulsed
 - - - - - - - - - - - - - - - - - 
 """

MeasurementType = 3

# Background/Measurement File Information
Bfilepath = ''
# Please enter this value in seconds - if no file leave the placeholder '1' value
Bduration = 1
Mduration = 1

# Bin size for histogramming - put in picoseconds
# This adjusts the resolution of your plots (note that if your bins are too small the data will look noisy
# and if your bins are too large you will lose the details of your plot)
bin_width_ps = 4
# For histogramming the T2 data
# From my understanding this value should be 1/sync rate or repetition rate of the laser
repetition_rate = 5 # in MHz
#time_window_ns = (1 / repetition_rate) * 1000 # in ns
time_window_ns = 250
# if the QD has a very quick delay what may happen is you plot will have data at the beginning
# and then a bunch of empty data up to your time window when this happens you can set this parameter to 
# true s.t. the histogramming takes the max(dtime) instead of your defined time window 
dtime_override = True

# Trimming Parameter - determines how much of the data the program should truncate
# Generally 1500 is good for lifetime and g2 autocorrelations measurements and
# 15000 is good for g2 pulsed measurements if you have a lot of data if not I wouldn't use this
trimming_threshold = 150000
trimming = False

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                               Fitting Parameters
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

"""
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
 Lifetime Fit Parameters
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
 Each fit array are in the form:

 [A1, Tau1, A2, Tau2, A3, Tau3]

 where A is the constant in front of an exponential term and tau is the time constant.
 the program is only meant to work with fits that go up to three exponential terms. If 
 you choose to plot one or two fits the program will plot fit1 or fit1 and fit2 
 respectively. 
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
"""

LNumFits = 3

Lfit1 = [500, 100, 50, 10, 20, 5]
Lfit2 = [500, 100, 50, 10, 0, 0]
Lfit3 = [500, 100, 0, 0, 0, 0]

Generic_Lifetime = r"$A_1 e^{-t/\tau_1} + A_2 e^{-t/\tau_2} + A_3 e^{-t/\tau_3}$"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# g2 specific variables
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# g2 CW Autocorrelation Fit Parameters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -

CW_Zero_Time_Offset = 55 # in nanoseconds
CFit1 = [0.5, 5]

"""
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
 g2 Pulsed Fit Parameters
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
 Each fit array are in the form:
 [Pulse_period_ns, y0, A1, Tau1, A2, Tau2, R]

 where A is the constant in front of each exponential term and tau is the time constant.
 R is a constant that is multiplied by each exponential. The program is designed to only 
 work with fits that go up to two exponential terms. If you choose to plot one or two fits 
 the program will plot fit1 or fit1 and fit2 respectively.
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - -
"""

Pulse_Period_ns = 200 # in nanoseconds
Pulsed_Zero_Time_Offset = 60 # in nanoseconds
Pfit1 = [Pulse_Period_ns, 1, 0.75, 15, 0.85, 20, 0.85]

# If you find that the fitting is not working it's best to manually define the number of peaks
# as this is usually the most common problem the program faces (the peak find algorithm that the program
# uses while is fairly reliable still makes mistakes) 
# If you don't want to manually set the number of peaks leave this variable as 0
Pulse_Peaks = 0

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
OO_Blinking = 0

# On/Off threshold - represented as a fraction of the peak intensity
OO_Threshold = 0.25
# Defining a time window for conversion from delay times to experiment time
# Smallest bin range should be around 10-100 ms
OO_bin_width_ms = 100

"""
 - - - - - - - - - - - - - - - - - 
           00_Measuretype
 - - - - - - - - - - - - - - - - - 
 0 = The program will apply a single exponential lifetime fit to the filtered data
 1 = The program will apply a pulsed fit to the filtered data
 - - - - - - - - - - - - - - - - - 
 """

OO_Measuretype = 1
# Lifetime fit in the form: [A1, Tau1, A2, Tau2, A3, Tau3]
OOLfit = [750, 50, 0, 0, 0, 0]
# Pulsed fit in the form: [Pulse_period_ns, y0, A1, Tau1, A2, Tau2, R]
OOPfit = [Pulse_Period_ns, 1, 0.75, 15, 0.75, 15, 0.85]