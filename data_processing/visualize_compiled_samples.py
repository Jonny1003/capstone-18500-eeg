import matplotlib.pyplot as plt
import os
import pandas
import numpy as np
from constants import *

# This file contains some plotting tools to visualize and verify data 
# is what we expect it to be.

FOLDER_NAME = "double_blink"
DIR = f"/Users/jonathanke/Documents/CMU/18500/data/compiled/{FOLDER_NAME}"


def plot_data(column, frame, name, save_loc):
    '''
    This function generates a simple plot of some input data against
    the timestamp.

    column: the column name of a pandas dataframe to plot on Y axis
    frame: the pandas dataframe to read data from
    name: title of the plot and y-axis
    save_loc: folder location to save to (relative to where this code is run)
    '''
    # plots time against specified column
    fig, axs = plt.subplots(figsize=(12, 4)) 
    frame.plot(x='Timestamp', y=column, ax=axs)
    axs.set_ylabel(name)
    axs.set_title(name)
    fig.savefig(save_loc)

def plot_af3_af4(frame, name, save_loc):
    '''
    This function generates a plot of af3 and af4 input data against
    the timestamp.

    frame: the pandas dataframe to read data from
    name: title of the plot
    save_loc: folder location to save to (relative to where this code is run)
    '''
    # plots time against specified column
    fig, axs = plt.subplots(figsize=(12, 4)) 
    frame.plot(x='Timestamp', y=[AF3, AF4], ax=axs)
    axs.set_ylabel('microV')
    axs.set_title(name)
    fig.savefig(save_loc)


if __name__ == "__main__":
    # modify code below to generate plots
    for i, fName in enumerate(os.listdir(DIR)):
        with open(DIR + "/" + fName) as f:
            data = pandas.read_csv(f, dtype=COLUMN_TYPES)
            plot_af3_af4(data, f"Sample {i}", f"visualizations/{FOLDER_NAME}_AF3_AF4/graph_{i}.png")
    




