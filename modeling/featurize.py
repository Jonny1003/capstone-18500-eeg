import os
import json
from re import L
import pandas 
import numpy as np
import sys
from datetime import datetime, timedelta
# use this with app.py
from modeling.constants import *
# use this when running this file using modeling.
# from constants import *

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
    # print(dataframe)
    '''gets peaks in every interval (in seconds) of the dataframe'''
    peaks = []
    interval_start = dataframe['Timestamp'].iloc[0]
    last_interval = dataframe['Timestamp'].iloc[-1]
    # print("start:", interval_start, last_interval)
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
        # print("intervals:",interval_start, last_interval)
    return peaks

def getNumAboveAveragePeaks(columnName, interval, dataframe):
    '''gets the number of intervals above the peaks average
       this acts as an approximation for the number of peaks 
       within the sample
    '''
    peaks = getPeaks(columnName, interval, dataframe)
    # print('peaks', peaks)
    if len(peaks) == 0:
        return 0
    avg = sum(peaks) / len(peaks)
    sq_err = [(p - avg)**2 for p in peaks]
    stddev = np.sqrt(sum(sq_err) / len(peaks))
    numHigher = 0
    for v in peaks:
        # get only the really high peaks
        if v > avg + 1.5 * stddev:
            numHigher += 1
    return numHigher

def variance(columnName, df):
    if df.shape[0] <= 1:
        return 0
    v = df[columnName].var()
    # print(v)
    return v

def median(columnName, df):
    return df[columnName].median()

def kurtosis(columnName, df):
    v = df[columnName].kurtosis()
    # print(v)
    if pandas.isna(v):
        return 0
    return v

def get_mins_maxs(columnName, df):
    prev = None 
    prevPrev = None 
    peaks, valleys = [], []
    for v in df[columnName]:
        if prev == None or prevPrev == None:
            pass
        elif prev < prevPrev and prev < v:
            valleys.append(prev)
        elif prev > prevPrev and prev > v:
            peaks.append(prev)
        prevPrev = prev 
        prev = v 
    return peaks, valleys

def get_second_max(columnName, df):
    peaks, _ = get_mins_maxs(columnName, df)
    first = getMaxOfColumn(columnName, df)
    out = 0
    for v in peaks:
        if v > out and v < first:
            out = v
    return out 

def peaks_variance(columnName, df):
    peaks, valleys = get_mins_maxs(columnName, df)
    return np.var(np.array(peaks + valleys)) 

def peaks_diff(columnName, df):
    peaks, valleys = get_mins_maxs(columnName, df)
    if len(peaks) == 0 or len(valleys) == 0:
        return 0
    avgPeak = sum(peaks) / len(peaks)
    avgValley = sum(valleys) / len(valleys)
    return avgPeak - avgValley

def sumTop2Peaks(columnName, df):
    peaks = getPeaks(columnName, .5, df)
    largest = max(peaks)
    sec_largest = 0
    for v in peaks:
        if v > sec_largest and v < largest:
            sec_largest = v
    return sec_largest/largest

def smooth(columnName, df, n):
    v = df.rolling(n).mean()
    # print(v)
    return v 

def get_maxes_tossed(columnName, df, threshold):
    prev = None 
    prevPrev = None 
    data = []
    for v in df[columnName]:
        if prev == None or prevPrev == None:
            pass
        elif prev < prevPrev and prev < v:
            data.append(prev)
        elif prev > prevPrev and prev > v:
            data.append(prev)
        prevPrev = prev 
        prev = v 
    out = []
    for i,curr in enumerate(data):
        if i > 0 and i < len(data)-1:
            prev = data[i-1]
            next = data[i+1]
            if curr > prev and curr > next:
                # peak 
                if not (abs(curr-prev) < threshold and abs(curr-next) < threshold):
                    out.append(curr)
    return out

def get_smooth_second_max(columnName, df, threshold):
    df = smooth(columnName, df, 15)
    peaks = get_maxes_tossed(columnName, df, threshold)
    if len(peaks) == 0:
        # don't care to compute peak... (below threshold)
        return df[columnName].median()
    first = max(peaks)
    out = 0
    for v in peaks:
        if v > out and v < first:
            out = v
    return out

def get_smooth_third_max(columnName, df, threshold):
    df = smooth(columnName, df, 15)
    peaks = get_maxes_tossed(columnName, df, threshold)
    if len(peaks) == 0:
        # don't care to compute peak... (below threshold)
        return df[columnName].median()
    second = get_smooth_second_max(columnName, df, threshold) 
    out = 0
    for v in peaks:
        if v > out and v < second:
            out = v
    return out



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
    'num_above_peaks_AF3': lambda df: getNumAboveAveragePeaks(AF3, .1, df),
    'num_above_peaks_AF4': lambda df: getNumAboveAveragePeaks(AF4, .1, df),
    'variance_AF3': lambda df: variance(AF3, df),
    'variance_AF4': lambda df: variance(AF4, df),
    'AF_scaled_ratio' : lambda df: 
        ((getMaxOfColumn(AF3, df)-median(AF3, df))/variance(AF3, df)) / 
        ((getMaxOfColumn(AF4, df)-median(AF4, df))/variance(AF4, df)),
    'AF_scaled_diff' : lambda df: 
        ((getMaxOfColumn(AF3, df))/variance(AF3, df)) - 
        ((getMaxOfColumn(AF4, df))/variance(AF4, df)),
    'AF_max_time_diff': lambda df: abs(getTimestampOfMax(AF3, df) - getTimestampOfMax(AF4, df)),
    'AF_max_diff': lambda df: getMaxOfColumn(AF3, df) - getMaxOfColumn(AF4, df),
    'AF_ratio': lambda df: getMaxOfColumn(AF3, df) / getMaxOfColumn(AF4, df),
    'AF3_median': lambda df: median(AF3, df),
    'AF4_median': lambda df: median(AF4, df),
    'AF_adj_max_ratio': lambda df: (getMaxOfColumn(AF3, df) - median(AF3, df)) / (getMaxOfColumn(AF4, df) - median(AF4, df)),
    'AF_adj_max_diff': lambda df: (getMaxOfColumn(AF3, df) - median(AF3, df)) - (getMaxOfColumn(AF4, df) - median(AF4, df)),
    'AF3_sum_2_peaks': lambda df: sumTop2Peaks(AF3, df),
    'AF4_sum_2_peaks': lambda df: sumTop2Peaks(AF4, df),
    'AF3_kurtosis' : lambda df: kurtosis(AF3, df),
    'AF4_kurtosis' : lambda df: kurtosis(AF4, df),
    'AF3_sum': lambda df: df[AF3].sum(),
    'AF4_sum': lambda df: df[AF4].sum(),
    'AF3_peaks_var' : lambda df: peaks_variance(AF3, df),
    'AF4_peaks_var' : lambda df: peaks_variance(AF4, df),
    'AF3_peaks_diff' : lambda df: peaks_diff(AF3, df),
    'AF4_peaks_diff' : lambda df: peaks_diff(AF4, df),
    'AF3_second_max' : lambda df: get_second_max(AF3, df),
    'AF4_second_max' : lambda df: get_second_max(AF4, df),
    'AF3_smooth_second_max' : lambda df: get_smooth_second_max(AF3, df, 100),
    'AF4_smooth_second_max' : lambda df: get_smooth_second_max(AF4, df, 200),
    'AF3_smooth_third_max' : lambda df: get_smooth_third_max(AF3, df, 80),
    'AF4_smooth_third_max' : lambda df: get_smooth_third_max(AF4, df, 80),
    'AF3_third_max_ratio' : lambda df: get_smooth_third_max(AF3, df, 80)/ getMaxOfColumn(AF3, df),
    'AF4_third_max_ratio' : lambda df: get_smooth_third_max(AF4, df, 80)/ getMaxOfColumn(AF4, df),
    'AF3_second_max_ratio' : lambda df: get_smooth_second_max(AF3, df, 100)/ getMaxOfColumn(AF3, df),
    'AF4_second_max_ratio' : lambda df: get_smooth_second_max(AF4, df, 200)/ getMaxOfColumn(AF4, df)
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

