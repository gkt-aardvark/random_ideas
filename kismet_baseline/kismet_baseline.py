#!/usr/bin/env python3

import sqlite3
import argparse
import pandas as pd

#command-line options
parser = argparse.ArgumentParser()

parser.add_argument('-i', action='store', dest='input_file',
			help='Specify the input file; must be Kismet DB',
			required=True)

parser.add_argument('-o', action='store', dest='output_file',
			help='Specify the output text file', default='baseline_macs.txt',
			required=False)
					
parser.add_argument('-t', action='store', dest='interval',
			help='Specify the time interval; default is 300 seconds (5 mins)',
			required=False)
					
results = parser.parse_args()

input_file = results.input_file
output_file = results.output_file
interval = results.interval + 's'#depending on length of capture, maybe 300 seconds is good


#set up connection to db
conn = sqlite3.connect(input_file)
conn.text_factory = lambda x: str(x, 'iso-8859-1')
query = 'SELECT ts_sec, sourcemac FROM packets;'

#read the data into a pandas dataframe, using chunksize in case the db is large
kismet = pd.DataFrame()
for chunk in pd.read_sql_query(query, conn, chunksize=10000):
	kismet = kismet.append(chunk)
conn.close()

#convert times to pandas datetimes
#you can do this with the initial SQL query, but whatever
min_ts = pd.to_datetime(kismet.ts_sec.min(), unit='s')
max_ts = pd.to_datetime(kismet.ts_sec.max(), unit='s')

#and... reset/round/whatever the timestamps to five-minute intervals via 'interval'
kismet.ts_sec = pd.to_datetime(kismet.ts_sec, unit='s').dt.floor(interval)

#get start and stop times and total number of intervals
total_intervals = len(kismet.ts_sec.value_counts())

#just checking the start/stop time and total number of intervals
print (f'[+] Start Time: {min_ts} Stop Time: {max_ts}')
print (f'[+] Number of intervals: {total_intervals}')

#drop exact duplicates, since we want only 1 occurrence of each device in each interval
kismet.drop_duplicates(inplace=True)

#this groups 
k1 = kismet.groupby(['sourcemac']).size().to_frame('intervals').sort_values('intervals', ascending=False)

#I'm gonna say that anything appearing in more than 95% of the intervals is baseline
#I put them in a list for later use
baseline_devices = k1[(k1.intervals >= 0.95 * total_intervals)]

#put in regular Python list and sort
baseline_list = list(baseline_devices.index)
baseline_list.sort()

print (f'[+] {len(baseline_list)} baseline devices present')

with open(output_file, 'w') as f:
	f.write (f'Start Time: {min_ts}\nStop Time: {max_ts}\n')
	f.write (f'Number of intervals: {total_intervals}\n')
	f.write (f'Interval size: {interval} seconds\n')
	f.write (f'Number of baseline macs: {len(baseline_list)}\n\n')
	macs = '\n'.join([mac for mac in baseline_list])
	f.write(macs)
	


