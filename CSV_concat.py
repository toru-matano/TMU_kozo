# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 11:00:48 2023

@author: toru1
"""
import codecs as cd
import numpy as np
import pandas as pd
import glob
import os
import sys
#encode type of import csv
ENCODE="cp932"

# %% FUNCTIONS
def FindHeader(filename, header, footer):
    # find header (after line of marker)
    nhead, nrows = 0, 0
    with cd.open(filename, "r", encoding=ENCODE, errors="ignore") as f:
        while True:
            line = f.readline().split(',')
            if line[0] == header:
                break
            nhead += 1
        while True:
            line = f.readline().split(',')
            if line[0] == footer:
                break
            nrows += 1
    return nhead, nrows


def ImportData(filename):
    print(filename)
    marker1 = '#EndHeader'
    marker2 = '#BeginMark'
    
    header, nrows = FindHeader(filename, marker1, marker2)
    with cd.open(filename, "r", ENCODE, "ignore") as csv_file:
        df = pd.read_csv(csv_file,
                         header=header-5,
                         nrows=nrows,
                         encoding = ENCODE
                         )
    #micro sec to sec
    timestep = df.iloc[0, 1]/10**4
    #difference between max and min
    ncols_max = [i for i in range(df.columns.size) if i>1 and (i-1)%3==1]
    ncols_min = [i for i in range(df.columns.size) if i>1 and (i-1)%3==2]
    diff = df.iloc[:, ncols_max].to_numpy() - df.iloc[:, ncols_min].to_numpy()
    df2 = pd.DataFrame(diff, index=df.iloc[:, 0])
    df2.index.name = "time"
    df2.columns = ["CH"+str(i+1) for i in range(df2.columns.size)]
    return df2

def main():
    # %% INITIAL SETTING
    #select all csv files in current directory
    InFileFolder = input("Type folder path: ")
    InFileName = "*.csv"
    #output file name
    OutFileFolder = 'out'
    OutFileName = 'out.csv'
    
    #%% MAIN
    outpath = os.path.join(InFileFolder, OutFileFolder)
    try:
        os.mkdir(outpath)
        print(outpath, "folder was created")
    except:
        pass
    outfilepath = os.path.join(outpath, OutFileName)
    
    #reading file
    print("Reading files...")
    path = os.path.join(InFileFolder, InFileName)
    DFs = [ImportData(filename) for filename in glob.glob(path)]
    print("Reading finished!")
    
    #concatenate all data and sort by index (time)
    DFs = pd.concat(DFs).sort_index()
    
    #convert time from 00:00:00
    starttime = DFs.index[0]
    newindex = pd.to_datetime(DFs.index) - pd.to_datetime(starttime)
    newindex = (pd.to_datetime('2000') + newindex).strftime('%d %H:%M:%S')
    DFs.index = newindex
    #save file
    print("Saving {} to {}".format(OutFileName, outpath))
    try:
        DFs.to_csv(outfilepath)
        print("done")
        return True
    except PermissionError:
        print("Unable to access to {}.\nClose the file before running".format(outfilepath))
        return False


if __name__ == "__main__":
    main()