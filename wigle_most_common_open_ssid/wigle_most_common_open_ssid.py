#!/usr/bin/env python3
# coding: utf-8

#I made this to take the csv files that are produced by the Wigle Wardriving app that are
#stored in the /sdcard/wiglewifi location on your Android phone and export out a list
#of the most-common open SSIDs for further use with WiFi Pineapple or whatever
#take the csv.gz files from that location, extract them, and put them in a folder

import os
import pandas as pd

#set base path wherever you want. Python handles forward slashes fine in Windows
base_path = './csv_files/'

#set initial pandas dataframe
entries = pd.DataFrame()

#loop through all csv wigle files in your base_path, add to entries
#btw, it seems iso-8859-1 works well with wigle csvs, better than utf8 for reading
#skiprows in pandas.read_csv skips the first row, leaving the header, which it will use
#wigle csvs have a first row of metadata for the upload itself, not useful for this
for file in os.listdir(base_path):
    if file.endswith('csv'):
        current_df = pd.read_csv(base_path + file, skiprows=1, encoding='ISO-8859-1')
        entries = entries.append(current_df)

#deduplicate based on mac and ssid, all else is irrelevant for this
unique_entries = entries.drop_duplicates(subset = ['SSID', 'MAC'])

#print top 25 open wifis to screen, because... printing is cool
#this filters by anything with [ESS] in the encryption type column, which is open
top_open = unique_entries[unique_entries.AuthMode=='[ESS]'].SSID.value_counts()[:25]
print (top_open)

#open file in base_path and write top 25 to file as plain text
#the .index.tolist() thingy just gets the names of the ssids, not their count
with open(base_path + 'open-ssid.txt', 'w') as fout:
	data = '\n'.join(top_open.index.tolist())
	fout.write(data)


