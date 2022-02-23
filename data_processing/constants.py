import numpy as np

# some universal constants/hyperparameters for processing

# special debug flag used to monitor processing pipeline
DEBUG = True

# location of raw data
RAW_DATA_LOC_FROM_SRC = "data/raw"

# location for compiled data (unfiltered data points)
COMPILED_DATA_LOC_FROM_SRC = "data/compiled"

# total time of each sample
TIME_DELAY = 3 # in seconds

# feed this into pandas from_csv function to get column datatypes parsed correctly
COLUMN_TYPES = {'Timestamp' : np.float64}

# column name aliases
AF3 = "EEG.AF3"
AF4 = "EEG.AF4"
PZ = "EEG.Pz"
