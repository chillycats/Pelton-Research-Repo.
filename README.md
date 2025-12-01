> [!CAUTION] This is a new but incomplete version of the program. Please proceed with caution and report any errors to Jaden Chilimigras at jchilim1@umbc.edu

# DQE Repository

DQE (Diagonistic program for Quantum Emitters) was designed as a user friendly option when analyzing data from the PicoQuant system in both T2 and T3 mode. DQE can be used to perform normalization, fitting, and data analysis on output files from the PicoQuant system to help build a more comprehensive understanding of the properties and stability of quantum emitters.

## Version History

The current version of DQE is able to read in data from T2 or T3 mode and perform a normalization and fitting of lifetime measurements made by the PicoHarp 300 hardware. Please see the resources folder for Matlab code provided by PicoQuant as a reference for the file format of the .ptu files specifically for the PicoHarp data system.

Lifetime code file is provided as an preliminary example of what the program will be able to do for T2 and T3 mode measurements.

## How to use DQE

To perform a fitting on any set of data collected from the PicoHarp 300 you enter the following command into the terminal:

```py
python DQE_main.py --ifile [paste file path here] --oname [output filename here]
```

This command will run DQE and with the default program settings that can be changed in the config file and save its output with the filename you gave on the command line. If you are using DQE for the first time you will need to paste the file path to your background measurement into the config file before you run the main program.

Currently, DQE does not take any user inputs beside the initial command. In the future there will be options to perform specific data analysis functions that will be chosen by the user's input.

If you forget this initial command you can always enter the following command into the terminal:

```py
python DQE_main.py --help
```

which will show you the command structure with help messages.

## Config File

You can think of the configuration file (config.py) as the settings menu for DQE. In it you will find variables that you will need to identify in order for DQE to operate smoothly. One of the most important variables you will find there is the variable called 'MeasurementType'. It is important that you keep this variable consistent with the file you are analyzing. If you are unsure or don't remember what kind of measurement select '0' as this will tell the program to only plot the data as it is read in from the file.

****************************


