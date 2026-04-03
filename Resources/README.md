> [!CAUTION] This is a new but incomplete version of the program. Please proceed with caution and report any errors to Jaden Chilimigras at jchilim1@umbc.edu

# Repository Detailed "Manual"

This README will provide all the details necessary for you to understand how this repository works. By the end of this README you will understand the basic structure of DQE, how each of its processes work, and the meaning behind many of the variables. Links to further resources that may be helpful are provided below:

- [PicoHarp 300 Manual](https://www.picoquant.com/dl_manuals/discontinued/PicoHarp300_DLL_Manual.pdf)
- [PicoQuant photon counting brochure](https://www.picoquant.com/images/uploads/downloads/photon_counting_brochure.pdf)

## Config File

The config file can be thought of as the control panel for the program. There are many different variables that you will see on this file. Whenever you go to analyze any dataset it is important to  ensure the settings in the config file are consistent with the measurements made. 

One of the most important variables that you should pay attention to is the MeasurementType variable. This variable can take on four different integer values, ranging from 0 to 3, each of which correspond to a specfic kind of measurement. Here's what each value means:

- 0: No specific measurement was made for the data set. The program will then only plot the raw data and perform no normalization or fitting of the data.
- 1: A lifetime measurement was made for the data set. The program will proceed to normalized and fit the data. It will then plot the fits and their respective residuals.
- 2: A g2 CW Autocorrelation measurement was made for the data set. The program will proceed to fit the data and plot its fit and the residuals.
- 3: A g2 Pulsed measurement was made for the data set. The program will proceed to fit the data and plot its fit and the residuals.

## Functions

This section of the "Manual" does a deep dive into all the different functions that are used by DQE to perform different tasks.

## "PTU_Reader"

PTU_Reader is the first function DQE calls and as the name suggests it is the function that reads in the data inputted by the user. This function will output all the neccessary information required for further analysis in the form of a dictionary. This includes the header information, any statistics, and photon arrival times/coicidence times. An example of the structure of the dictornary is seen below:

```py
# T3 and dat mode specific 
result_dict = {
            'header': Header_Data,
            'metadata': {
                'record_type': TTResultFormat_TTTRRecType,
                'total_records': TTResult_NumberOfRecords,
                'resolution': MeasDesc_Resolution,
                'global_resolution': MeasDesc_GlobalResolution,
                'is_t2_mode': isT2
            },
            'photons': photons_array,
            'markers': markers_array, 
            'overflows': overflows_array,
            'photon_times': photon_times,
            'T2channel': channel,
            'statistics': {
                'photons': photon_count,
                'markers': marker_count,
                'overflows': overflow_count
            }
        }
```

The dictionary structure above is generic for T3 and any .dat files. If a measurement is taken in T2 mode there will be additional items within the dictionary as seen below:

```py
# T2 TCSPC Histogram Data
'tcspc': {
    'histogram': t2_histogram_data['histogram'],
    'time_axis': t2_histogram_data['time_axis'],
    'histogrammed_photons': t2_histogram_data['histogrammed_photons'],
    'sync_times': t2_histogram_data['sync_times'],
    'signal_times': t2_histogram_data['signal_times'],
    'parameters': {
        'sync_channel': t2_histogram_data['sync_channel'],
        'signal_channel': t2_histogram_data['signal_channel'],
        'time_window_ns': t2_histogram_data['time_window_ns'],
        'bin_width_ps': t2_histogram_data['bin_width_ps'],
        'n_bins': t2_histogram_data['n_bins']
    },
    'statistics': {
        'sync_rate_MHz': t2_histogram_data['sync_rate_MHz'],
        'photon_rate_MHz': t2_histogram_data['photon_rate_MHz'],
        'counts_per_sync': t2_histogram_data['counts_per_sync'],
        'n_sync_pulses': t2_histogram_data['n_sync_pulses'],
        'n_signal_photons': t2_histogram_data['n_signal_photons'],
        'histogramming_efficiency': t2_histogram_data['histogramming_efficiency']
    }
}
```

## "PTU_Normalize"

Before the program normalizes the data it will first subtract the background data from the experimental data; also accounting for the possible different durations of each measurement file. If the user selected an integer from 1 to 3 for the MeasurementType variable in the config file the program will normalize the data with respect to the specific kind of measurements made. Currently, there are three different options that the user can select for the data to be normalized as listed below:

1. Lifetime Measurement Mode

The program will normalize the data in accordance with the equation:

```math
\text{Normalized Data} = \frac{\text{Main Data}}{\text{Maximum Value of the Main Data}}
```

2. Both g2 Measurement Modes

Since the normalization for the data is the same regardless of the specific kind of g2 measurmenet the program will normalize the data in accordance with the equation:

```math
\text{Normalized Data} = \frac{\text{Main Data}}{N_{\text{photons, 1}}*N_{\text{photons, 2}}} * \left(\frac{\text{Main Data Duration (ps)}}{\text{Bin Size (ps)}}\right)
```

## "PTU_Fitting"

After the data is normalized the program will then fit the data in accordance with the measurement mode chosen. The equations for each mode are given by:

```math
\begin{align}
    &= A_1 e^{-t/\tau_1} + ... + A_n e^{-t/\tau_n} \\

    &= 1 - A_1 e^{t/\tau_1} \\

    &= y_0 + a_1(R e^{-|t/\tau_1|}) + ... + a_n(R e^{-|t/\tau_n|})
\end{align}
```
