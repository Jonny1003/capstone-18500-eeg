import csv 
import os
import json
import pandas 
import numpy as np
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# constants
DEBUG = True
RAW_DATA_LOC_FROM_SRC = "data/raw"
COMPILED_DATA_LOC_FROM_SRC = "data/compiled"
TIME_DELAY = 3 # in seconds
COLUMN_TYPES = {'Timestamp' : np.float64}
AF3 = "EEG.AF3"
AF4 = "EEG.AF4"


def findRawDataFolder(folderName, depth_from_src=1):
    '''Finds the folder within raw data with folderName from this file location'''
    # iterate back to src folder
    if DEBUG:
        print("\nSourcing raw data folder...\n")
    currDir = os.getcwd()
    for _ in range(depth_from_src):
        currDir = os.path.dirname(currDir)
    # search for folderName
    dir_loc = os.path.join(currDir, RAW_DATA_LOC_FROM_SRC + '/' + folderName)
    if (os.path.isdir(dir_loc)):
        return dir_loc
    # folder not found, we have a problem...
    elif DEBUG: 
        print(f"Folder {folderName} not found when finding raw data folder!")
    return None

def organizeRawData(dirLoc):
    if DEBUG:
        print("\nOrganizing data files...\n")
    # walks through the specific directory and creates grouping
    # of the directory data
    groups = []
    data = sorted(os.listdir(dirLoc))
    i = 0
    while i < len(data):
        jsonFile, dataFile, intervalFile = None, None, None
        fileName = "NonExistentFileGroup"
        # check if the first file is json
        if data[i].endswith(".json"):
            jsonFile = data[i]
            fileName = jsonFile.rstrip(".json")
            i += 1
        elif DEBUG:
            print("Could not locate json file containing markers information.")
        if i == len(data):
            if DEBUG:
                print(f"Could not locate csv files containing raw and marker data for {fileName}.")
            break
        if data[i].endswith(".csv") and data[i].startswith(fileName):
            dataFile = data[i]
            i += 1
        elif DEBUG:
            print("Could not locate csv file containing raw data.")
        if i == len(data):
            if DEBUG:
                print(f"Could not locate csv files containing marker data for {fileName}.")
            break
        if data[i].endswith(".csv") and data[i].startswith(fileName):
            intervalFile = data[i]
            i += 1
        elif DEBUG:
            print("Could not locate csv file containing markers information.")
        if jsonFile and dataFile and intervalFile:
            groups.append((jsonFile, dataFile, intervalFile))
        elif DEBUG:
            print(f"Could not create group for {fileName}")

    if DEBUG:
        print("Groups created:")
        for group in groups:
            print("\t" + str(group))
    return groups

def parseData(dir_loc, groupings, label):
    '''converts the raw data into data points
    '''
    if DEBUG:
        print("\nParsing data...\n")
    out = []
    for markerJson, dataCsv, _ in groupings:
        with open(dir_loc + "/" + markerJson) as markerFile, open(dir_loc + '/' + dataCsv) as dataFile:
            markerData = json.load(markerFile)
            rawData = pandas.read_csv(dataFile, skiprows=1, dtype=COLUMN_TYPES)

            prevMarker = ""
            for marker in markerData['Markers']:
                if marker['label'] == 'invalid':
                    if prevMarker == label and len(out):
                        # remove the previous data point because it is invalid
                        badFrame = out.pop()
                        if DEBUG:
                            print("Removing invalid data point:")
                            print(badFrame)
                elif marker['label'] == label:
                    startTime = datetime.fromisoformat(marker['originalStartDatetime'])
                    endTime = startTime + timedelta(seconds=TIME_DELAY)
                    startTimeStamp = datetime.timestamp(startTime)
                    endTimeStamp = datetime.timestamp(endTime)
                    next3Seconds = rawData.loc[(rawData['Timestamp'] >= startTimeStamp) &
                        (rawData['Timestamp'] <= endTimeStamp)]
                    out.append(next3Seconds)
                elif DEBUG:
                    print(f"Found an unrecognized marker label {marker['label']}!")
                prevMarker = marker['label']
    return out

def save_compiled_data_points(folder_name, data_points, depth_from_src=1):
    if DEBUG:
        print("\nSaving compiled data points...\n")
    currDir = os.getcwd()
    for _ in range(depth_from_src):
        currDir = os.path.dirname(currDir)
    # search for folderName
    dir_loc = os.path.join(currDir, COMPILED_DATA_LOC_FROM_SRC + '/' + folder_name)
    if (not os.path.isdir(dir_loc)):
        if DEBUG:
            print("Destination folder does not exist! Aborting data export process...")
        return 
    for point in data_points:
        # get the top timestamp
        timestamp = point.iat[0,0]
        point.to_csv(f"{dir_loc}/{folder_name}_{timestamp}.csv")

def compile_raw_data(folder_name, marker_label):
    dir_loc = findRawDataFolder(folder_name)
    data_groups = organizeRawData(dir_loc)
    data_points = parseData(dir_loc, data_groups, marker_label)
    save_compiled_data_points(folder_name, data_points)


CMD_ARG_FOLDER = "FOLDER="
CMD_ARG_MARKER = "MARKER="

if __name__ == "__main__":
    args = sys.argv
    folder_name, marker_label = None, None
    for arg in args:
        if CMD_ARG_FOLDER in arg:
            folder_name = arg.lstrip(CMD_ARG_FOLDER).strip()
        elif CMD_ARG_MARKER in arg:
            marker_label = arg.lstrip(CMD_ARG_MARKER).strip()
    if not folder_name or not marker_label:
        print("Provided bad arguments.")
        print(f"Expecting> python3 raw_to_compiled.py {CMD_ARG_FOLDER}<folder name> {CMD_ARG_MARKER}<marker label>")
        sys.exit(-1)
    compile_raw_data(folder_name, marker_label)