import matplotlib.pyplot as plt
import os
import pandas
import numpy as np

AF3 = "EEG.AF3"
AF4 = "EEG.AF4"
COLUMN_TYPES = {'Timestamp' : np.float64}
FOLDER_NAME = "double_blink"
DIR = f"/Users/jonathanke/Documents/CMU/18500/data/compiled/{FOLDER_NAME}"

def plot_data(column, frame, name, save_loc):
    # plots time against specified column
    fig, axs = plt.subplots(figsize=(12, 4)) 
    frame.plot(x='Timestamp', y=column, ax=axs)
    axs.set_ylabel('microV')
    axs.set_title(name)
    fig.savefig(save_loc)

def plot_af3_af4(frame, name, save_loc):
    # plots time against specified column
    fig, axs = plt.subplots(figsize=(12, 4)) 
    frame.plot(x='Timestamp', y=[AF3, AF4], ax=axs)
    axs.set_ylabel('microV')
    axs.set_title(name)
    fig.savefig(save_loc)


for i, fName in enumerate(os.listdir(DIR)):
    with open(DIR + "/" + fName) as f:
        data = pandas.read_csv(f, dtype=COLUMN_TYPES)
        plot_af3_af4(data, f"Sample {i}", f"{FOLDER_NAME}_AF3_AF4/graph_{i}.png")
    




