> [!CAUTION] This is a new but incomplete version of the program. Please proceed with caution and report any errors to Jaden Chilimigras at jchilim1@umbc.edu

# Pelton Research Repository

DQUE (Diagonistic Program for Quantum Emitters) was designed as a user friendly option when analyzing data from the PicoQuant system in both modes (T2 and T3). Currently the program only handles data gathered in T2 mode - most of the current updates are finishing touches on the g2 measurement normalization and fitting functions. Please note the Overview below that goes in depth into the structure of the program and what each file does.

****************************

# Overview

* [Overall Structure](#overall-structure)
    * [Program Structure](#program-structure)
    * [Function Files](#function-files)
        * [T2-configure-datafile.py](#T2-configure-datafile.py)
        * [T2-fitting.py](#T2_fitting.py)
        * [T2-normalize.py](#T2_normalize.py)
        * [T2-plotting.py](#T2_plotting.py)
    * [Program Jupytr Files](#program-jupytr-files)
* [Running?]


## Overall Structure

### Program Structure

### Function Files

Below are breif descriptions of what functions are contained within each file and their details. This includes things like the parameters for the functions, what they return, and how they function.

#### T2-configure-datafile.py

The T2-configure-datafile python file contains functions that are independent of the measurement made excluding the time_array_construct function. The goal of this function to initialize everything (ie. reading in the experiment information, retrieving the data, trimming the data, and creating the time array). Currently, the functions within this python file are the reading_file, retrieve_data, threshold_trim_function, and time_array_construction.

Below are breif descriptions of each function including important information such as paramaters, return values, and a general description of what the function accomplishes.

* reading_file: The main goal of reading_file is to retrieve the measurement information from the data file inputted by the user. This function saves information such as the date, time, ns_channel, and channels_per_curve in an array. The only parameter for this function is the file path and it returns an array of the previously stated information.

#### T2-fitting.py

#### T2-normalize.py

#### T2-plotting.py
