# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY LIBRARIES
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
import struct
import numpy as np
import datetime
import tkinter as tk
import argparse
import os

from pathlib import Path
from tkinter import filedialog
from typing import Dict, Any, Tuple

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#               IMPORTING THE NECESSARY FUNCTIONS
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#                           MAIN PROGRAM
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

def parse_arguments():
    """
    Parses command line arguments and returns all arguments.
    """
    parser = argparse.ArgumentParser(
        description='Process .ptu data files'
    )
    
    parser.add_argument('--input_filepath', 
                       required=True,
                       type=str,
                       help='Path to the input PTU file')
    
    parser.add_argument('--output_filename',
                       required=True,
                       type=str,
                       help='Name for the output file')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.input_filepath):
        print(f"Error: File '{args.filepath}' does not exist")
        exit(1)

    args = parser.parse_args()
    return args.input_filepath, args.output_filename

if __name__ == '__main__':
    filepath, output_filename = parse_arguments()