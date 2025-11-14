> [!CAUTION] This is a new but incomplete version of the program. Please proceed with caution and report any errors to Jaden Chilimigras at jchilim1@umbc.edu

# DQE Repository

DQE (Diagonistic program for Quantum Emitters) was designed as a user friendly option when analyzing data from the PicoQuant system in both T2 and T3 mode. DQE can be used to perform normalization, fitting, and data analysis on output files from the PicoQuant system to help build a more comprehensive understanding of the properties and stability of quantum emitters.

## Version History

The current version of DQE is able to read in data from T2 or T3 mode and perform a normalization and fitting of lifetime measurements made by the PicoHarp 300 hardware. Please see the resources folder for Matlab code provided by PicoQuant as a reference for the file format of the .ptu files specifically for the PicoHarp data system.

Lifetime code file is provided as an preliminary example of what the program will be able to do for T2 and T3 mode measurements.

## How to use DQE

To perform a fitting on any set of data collected from the PicoHarp 300 you enter the following command into the terminal,

'''
python DQE-main.py --main-filepath [paste file path here]
'''

This command will run DQE with the default program settings that can be changed in the config file. If you are using DQE for the first time you will need to input your background measurement's filepath into the config file before you run the main program.

****************************


