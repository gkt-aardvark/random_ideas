#!/usr/bin/env python3
# coding: utf-8

'''pandas thingy to determine in how many time intervals the devices in a
kismet db are present. this is to see which devices are the 'baseline'
devices so we could then filter them. In general, it just tells us how
often a device is present'''

import sqlite3
import json
import pandas as pd

#set up connection to db, make sure path is correct
conn = sqlite3.connect('guate.kismet')
query = 'SELECT ts_sec, sourcemac FROM packets;'

#read the data into a dataframe
kismet = pd.read_sql_query(query, conn)
conn.close()

#set a reasonable interval, could be seconds, minutes, whatever
#I'm going with 300s, since 5 minutes is a reasonable time
#to give every device a chance to be "present"
interval = '300s'

#get start and stop times just because
min_ts = pd.to_datetime(kismet.ts_sec.min(), unit='s')
max_ts = pd.to_datetime(kismet.ts_sec.max(), unit='s')

#reset/round/whatever the timestamps to five-minute intervals via our interval
kismet.ts_sec = pd.to_datetime(kismet.ts_sec, unit='s').dt.floor(interval)

#get start and stop times and total number of intervals
total_intervals = len(kismet.ts_sec.value_counts())

print ('Start Time: {} Stop Time: {}'.format(min_ts, max_ts))
print ('Number of intervals: {}'.format(total_intervals))

#since our dataframe only has a rounded timestamp and a mac
#when we drop duplicates, that will leave us with 1 occurrence of each mac per interval
kismet.drop_duplicates(inplace=True)

#group the dataframe by mac, count (size) how many intervals it appears in
#and sort in descending order, showing most-active (baseline) devices at the top
#this could be used to filter, identify, whatever...
k1 = kismet.groupby('sourcemac').size().to_frame('intervals').sort_values('intervals', ascending=False)

#I'm gonna say that anything appearing in more than 95% of the intervals is baseline
baseline_devices = k1[(k1.intervals >= 0.95 * total_intervals)]

#do something with them
print (baseline_devices.index.values)




