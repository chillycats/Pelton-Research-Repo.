#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

""""
confirmation

This function works by taking a user input and checking to see if the input is what the user desired. If it's not the function will
keep the user in a loop until they enter the correct input. 

Args:
    user_input: user input that will be checked
    prompt: what the desired input is

Returns:
    user_input: either the original or updated value of the user's input
"""

def confirmation(prompt):
    # defining Boolean value to keep the user in a loop
    valid_input = False
    # while loop that will execute until the user inputs the correct input
    while valid_input == False:
        user_input = input(f"Please provide the {prompt}.")

        # check for termination input
        terminate = terminate_program(user_input)
        if terminate == True:
            return '/'

        print("Please enter 'y' or 'n'.")
        print("You entered:", user_input)
        confirmation = input("Is this the correct input?")

        # check for termination input
        terminate = terminate_program(confirmation)
        if terminate == True:
            return '/'

        confirmation = confirmation.lower()
        if confirmation == 'y':
            return user_input
        else:
            print("Please re-enter the correct input for", prompt) 