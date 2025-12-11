# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  
#                         Configuration Parameters for DQE
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

# - - - - - - - - - - - - - - - - - 
# Measurement Type
# - - - - - - - - - - - - - - - - - 
# 0 = None of the measurement types listed below will consequentially only plot the 'raw' data
# 1 = Lifetime Measurement
# 2 = g2 CW Autocorrelations
# 3 + g2 Pulsed
# - - - - - - - - - - - - - - - - - 

MeasurementType = 0

# Background File Information
bckgrd_filepath = ''
# Please enter this value in seconds
bckgrd_duration = 1

# Trimming Parameter - determines how much of the data DQE should truncate
trimming_threshold = 150

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                               Fitting Parameters
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  

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

LNumFits = 3

Lfit1 = [500, 100, 50, 10, 20, 5]
Lfit2 = [500, 100, 50, 10, 0, 0]
Lfit3 = [500, 100, 0, 0, 0, 0]


# g2 CW Autocorrelation Fit Parameters

# g2 Pulsed Fit Parameters