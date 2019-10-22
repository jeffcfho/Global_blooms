#!/usr/bin/python

import pandas as pd
from IPython.display import display

def print_full(x):
    # prints all rows in dataFrame, useful for seeing all of the data
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')
    
def display_full(x):
    # prints all rows in dataFrame, useful for seeing all of the data
    pd.set_option('display.max_rows', len(x))
    display(x)
    pd.reset_option('display.max_rows')