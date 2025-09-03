#importing necessary libraries
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

""""
terminate_program

This function works by taking a user input and checking to see if the input is 'esc', if not then it returns the Boolean
value of False so that the program will continue to run. Otherwise, it will return the Boolean value of True so that the
program will exit the while loop.

Args:
    confirm_term: the user input in response to a prompt

Returns:
    Boolean value depedent on a given condition
"""

def terminate_program(confirm_term):
    if confirm_term == '/':
        terminate = True
    else: 
        terminate = False
    return terminate