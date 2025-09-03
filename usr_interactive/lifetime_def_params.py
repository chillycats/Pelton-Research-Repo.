#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

"""
T2_lifetime_def_fits

The defining_fits function's main goal is to return a list of the constants and time constants that will be used for the user's
expenential fit. It also does not take any input parameters. This function may be called multiple times if the user wishes to 
defined multiple exponential fits.

Args:
    N/A

Returns:
    [num_of_terms, parameters]
    num_of_terms: the number of terms in the exponential fit
    parameters: the constants and time constants for each exponential term in the form: [A1, tau1, A2, tau2, A3, tau3]
"""

def T2_lifetime_def_parameters():
    # determines the number of terms in the exponential fit
    valid_input = False
    while valid_input == False:
        num_of_terms = input("Please enter an integer between one and three for the number of terms you would like to include in your fit.")
    
        # checking to see if the user terminated the program
        terminate = terminate_program(num_of_terms)
        if terminate == True:
            return terminate
        
        print("Number of terms in exponential fit:", num_of_terms)
        print("Please enter 'y' or 'n'.")
        confirmation1 = input("Is this the correct number of terms for your exponential fit?")
        confirmation1 = confirmation1.lower()

        # checking to see if the user terminated the program
        terminate = terminate_program(confirmation1)
        if terminate == True:
            return terminate
        
        if confirmation1 == 'y':
            break
        else:
            print("Please re-enter the correct number of exponential terms you would like in your fit.")
    
    num_of_terms = int(num_of_terms)

    parameters = []

    # executes a for loop to determine each of values for the set number of exponential terms
    for n in range(num_of_terms):
        term = n+1
        print("For your n = ", term," exponential term:")

        # while loop to ensure the correct input is inputted
        valid_input = False
        while valid_input == False:
            A = input("What would you like your A constant to be?")
        
            # checking to see if the user terminated the program
            terminate = terminate_program(A)
            if terminate == True:
                return terminate
        
            print("A",term,"=", A)

            print("Please enter 'y' or 'n'.")
            confirmation2 = input("Is this the correct value for your A constant for your exponential fit?")
            confirmation2 = confirmation2.lower()

            # checking to see if the user terminated the program
            terminate = terminate_program(confirmation2)
            if terminate == True:
                return terminate
        
            if confirmation2 == 'y':
                A = float(A)
                parameters.append(A)
                break
            else:
                print("Please re-enter the correct number for the A constant for your n =", term,"in your exponential.")
        
        # while loop to ensure the correct input is inputted
        valid_input = False
        while valid_input == False:
            tau = input("What would you like your tau constant to be?")
    
            #checking to see if the user terminated the program
            if terminate == True:
                return terminate
            
            print("Tau",term,"=",tau)

            print("Please enter 'y' or 'n'.")
            confirmation3 = input("Is this the correct value for your time constant for your exponential fit?")
            confirmation3 = confirmation3.lower()

            # checking to see if the user terminated the program
            terminate = terminate_program(confirmation3)
            if terminate == True:
                return terminate
            
            if confirmation3 == 'y':
                tau = float(tau)
                parameters.append(tau)
                break
            else:
                print("Please re-enter the correct number for the time constant for your n =", term," in your exponential fit.")

    #creates the list of the int of the number of terms and their given parameters - the num_of_terms will be used later when plotting the data
    exp_fit_info = [num_of_terms, parameters]
    return exp_fit_info