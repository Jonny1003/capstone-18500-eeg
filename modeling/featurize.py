import os
import json
import pandas 
import numpy as np
import sys
from datetime import datetime, timedelta
from constants import *

# This file contains functions for generating feature vectors of a compiled data set.

# functions for computing a specific feature out of a compiled data point
def getMaxOfColumn(columnName, dataframe):
    '''gets the max of a specified column'''
    column = dataframe[columnName]
    return column.max()

def getTimestampOfMax(columnName, dataframe):
    '''gets the time stamp of when columnName is max'''
    return dataframe.at[dataframe[columnName].idxmax(), 'Timestamp']

def getMeanOfColumn(columnName, dataframe):
    '''gets the mean of a specified column'''
    return dataframe[columnName].mean()

def getNthLargestOfColumn(columnName, n, dataframe):
    '''gets the nth largest value in the specified column'''
    topN = dataframe[columnName].nlargest(n, keep='all')
    return topN.iloc[-1]

def getPeaks(columnName, interval, dataframe):
    '''gets peaks in every interval (in seconds) of the dataframe'''
    peaks = []
    interval_start = dataframe.at[0, 'Timestamp']
    last_interval = dataframe['Timestamp'].iloc[-1]
    while interval_start < last_interval:
        # print(interval_start)
        interval_end = interval_start + interval
        # print(interval_start, interval_end)
        # print(interval_end)
        subframe = dataframe.loc[
            (dataframe['Timestamp'] <= interval_end) & 
            (dataframe['Timestamp'] > interval_start)
        ]
        # print(subframe)
        peak = subframe[columnName].max()
        # print(peak)
        peaks.append(peak)
        interval_start = interval_end
    return peaks

def getNumAboveAveragePeaks(columnName, interval, dataframe):
    '''gets the number of intervals above the peaks average
       this acts as an approximation for the number of peaks 
       within the sample
    '''
    peaks = getPeaks(columnName, interval, dataframe)
    # print(peaks)
    avg = sum(peaks) / len(peaks)
    sq_err = [(p - avg)**2 for p in peaks]
    stddev = np.sqrt(sum(sq_err) / len(peaks))
    numHigher = 0
    for v in peaks:
        # get only the really high peaks
        if v > avg + 2 * stddev:
            numHigher += 1
    return numHigher

def variance(columnName, df):
    v = df[columnName].var()
    # print(v)
    return v

def median(columnName, df):
    return df[columnName].median()


# dictionary of feature functions to compute a statistic from a single compiled data point
FEATURE_LIBRARY = {
    'AF3_max': lambda df: getMaxOfColumn(AF3, df),
    'AF4_max': lambda df: getMaxOfColumn(AF4, df),
    'Pz_max': lambda df: getMaxOfColumn(PZ, df),
    'AF3_time_of_max': lambda df: getTimestampOfMax(AF3, df),
    'AF4_time_of_max': lambda df: getTimestampOfMax(AF4, df),
    'Pz_time_of_max': lambda df: getTimestampOfMax(PZ, df),
    'AF3_second_largest': lambda df: getNthLargestOfColumn(AF3, 2, df),
    'AF4_second_largest': lambda df: getNthLargestOfColumn(AF4, 2, df),
    'Pz_second_largest': lambda df: getNthLargestOfColumn(PZ, 2, df),
    'AF3_mean': lambda df: getMeanOfColumn(AF3, df),
    'AF4_mean': lambda df: getMeanOfColumn(AF4, df),
    'Pz_mean': lambda df: getMeanOfColumn(PZ, df),
    'peaks': lambda df: getPeaks(AF3, .25, df),
    'num_above_peaks_AF3': lambda df: getNumAboveAveragePeaks(AF3, .1, df),
    'num_above_peaks_AF4': lambda df: getNumAboveAveragePeaks(AF4, .1, df),
    'variance_AF3': lambda df: variance(AF3, df),
    'variance_AF4': lambda df: variance(AF4, df),
    'AF_max_time_diff': lambda df: abs(getTimestampOfMax(AF3, df) - getTimestampOfMax(AF4, df)),
    'AF_max_diff': lambda df: getMaxOfColumn(AF3, df) - getMaxOfColumn(AF4, df),
    'AF_ratio': lambda df: getMaxOfColumn(AF3, df) / getMaxOfColumn(AF4, df),
    'AF3_median': lambda df: median(AF3, df),
    'AF4_median': lambda df: median(AF4, df),
    'AF_adj_max_ratio': lambda df: (getMaxOfColumn(AF3, df) - median(AF3, df)) / (getMaxOfColumn(AF4, df) - median(AF4, df)),
    'AF_adj_max_diff': lambda df: (getMaxOfColumn(AF3, df) - median(AF3, df)) - (getMaxOfColumn(AF4, df) - median(AF4, df))
}

def getPathToCompiledDataSet(folderName, depth_from_src=1):
    '''Source the path to the compiled data set'''
    if DEBUG:
        print(f"\nSourcing compiled data folder {folderName}...\n")

    path = os.getcwd()
    for _ in range(depth_from_src):
        path = os.path.dirname(path)
    path = "/".join((path, COMPILED_DATA_LOC_FROM_SRC, folderName))
    if (os.path.isdir(path)):
        return path 
    elif DEBUG:
        print("Folder could not be found!")
    return None 

def computeFeatures(folderPath, features, label):
    '''
    Creates a table where each row is a feature vector with the features in 
    the first N-1 rows and the label for the vector in the last row. 
    '''
    if DEBUG:
        print(f"\nComputing features {features} on data set in {folderPath}\n")
    data = os.listdir(folderPath)
    featureTable = pandas.DataFrame(columns=(features + ['label']))
    for rInd, file in enumerate(data):
        df = pandas.read_csv(folderPath + '/' + file, dtype=COLUMN_TYPES)
        row = []
        for f in features:
            if f not in FEATURE_LIBRARY:
                if DEBUG:
                    print(f"Feature {f} is not mapped in the feature library! \
                        You must define and map a feature with its corresponding \
                        function in the feature library before using it!")
                print("Error in creating features... Aborting!")
                return None
            func = FEATURE_LIBRARY[f]
            row.append(func(df))
        # the label for this vector
        row.append(label)
        featureTable.loc[rInd] = row 
    return featureTable

def vectorizeColumn(df, column, bound):
    # turns an entire column of data into a single horizontal vector
    # of length bound for each compiled datapoint in folderPath
    row = list(df.loc[column].iloc[:bound])
    return row

# Example usage:

################################################
# Differentiate blink vs no blink

# features = ["AF3_max", "AF4_max", "AF3_time_of_max", "AF4_time_of_max"]
# src1 = getPathToCompiledDataSet("blink")
# f1 = computeFeatures(src1, features, "blink")
# src2 = getPathToCompiledDataSet("baseline")
# f2 = computeFeatures(src2, features, "baseline")
# featureTable = pandas.concat([f1, f2])
# featureTable.to_csv("../data/featurized/sandbox/blink_baseline_max.csv")

################################################
# Differentiate baseline vs anything else

# features = ["AF3_max", "AF4_max", "AF3_time_of_max", "AF4_time_of_max"]
# featureTable = None 
# data = []
# for artifact in ['blink', 'double_blink', 'left_wink', 'right_wink', 'triple_blink']:
#     src = getPathToCompiledDataSet(artifact)
#     more_data = computeFeatures(src, features, "artifact")
#     data.append(more_data)

# src2 = getPathToCompiledDataSet("baseline")
# baseline = computeFeatures(src2, features, "baseline")
# featureTable = pandas.concat(data + [baseline])

# featureTable.to_csv("../data/featurized/sandbox/artifact_baseline_max.csv")

################################################
# Differentiate baseline vs anything else trial 2

# features = ['AF3_max', 'AF4_max', 'num_above_peaks_AF3', 'num_above_peaks_AF4', 'variance_AF3', 'variance_AF4']
# featureTable = None 
# data = []
# for artifact in ['blink', 'double_blink', 'left_wink', 'right_wink', 'triple_blink']:
#     src = getPathToCompiledDataSet(artifact)
#     more_data = computeFeatures(src, features, artifact)
#     data.append(more_data)

# src2 = getPathToCompiledDataSet("baseline")
# baseline = computeFeatures(src2, features, "baseline")
# featureTable = pandas.concat(data + [baseline])

# featureTable.to_csv("../data/featurized/sandbox/all_features_compute.csv")

################################################
# Differentiate blink and left wink vs right wink

# if __name__ == '__main__':
#     features = ['AF3_max', 'AF4_max', 'AF_max_time_diff', 
#         'AF_max_diff', 'AF_ratio', 
#         'AF_adj_max_diff', 'AF_adj_max_ratio']
#     featureTable = None 
#     data = []
#     for artifact in ['blink', 'left_wink', 'right_wink']:
#         src = getPathToCompiledDataSet(artifact)
#         more_data = computeFeatures(src, features, artifact)
#         data.append(more_data)

#     featureTable = pandas.concat(data)
#     featureTable.to_csv("../data/featurized/sandbox/blink_winks.csv")

