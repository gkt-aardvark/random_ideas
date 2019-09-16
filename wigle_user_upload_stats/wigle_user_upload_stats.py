#!/usr/bin/env python3
# coding: utf-8

import requests
import sys
import pandas as pd
from requests.auth import HTTPBasicAuth

name = 'INSERT OWN API NAME HERE'
password = 'INSERT OWN API PASSWORD HERE'

#set initial values
uploads = pd.DataFrame() #empty dataframe
start = 0
end = 100


def transid_dt(transid):
	'''function to convert transid into a datetime
		wigle's stats are based on their timezone and
		the transid is from their timezone'''
	ts = pd.to_datetime(transid[0:8])
	return ts

#if you've been on wigle a while, this part will take the longest
#wigle allows paginated results, 100 at a time
print ('Downloading user uploads stats...')
while True:
	request = requests.get(f"https://api.wigle.net/api/v2/file/transactions?pagestart={start}&pageend={end}",
							auth=HTTPBasicAuth(name, password))
	try:
		query = request.json()
	except:
		print ('[-] Authentication incorrect. Exiting...')
		sys.exit(1)
	if not (len(query['results']) == 0):
		for result in query['results']:
			uploads = uploads.append(pd.DataFrame(result, index=[0]))
		start += 100
		end = start + 100
		print (f"Downloaded {len(uploads)} so far...")
	else:
		break



#set a new column 'day' which is a datetime from the transid
uploads['day'] = uploads.transid.apply(transid_dt)
uploads.set_index('day', inplace=True)

#drop useless columns... well, useless for this
uploads.drop(columns = ['fileName',
			'fileSize', 
			'fileLines',
			'status', 
			'lastupdt',
			'percentDone',
			'timeParsing', 
			'firstTime'], 
		inplace=True)

#drop duplicates, just in case
uploads.drop_duplicates(inplace=True)

#group by month and create new dataframe out of the sum of summable columns
#pandas will only sum the things that make sense, dropping the rest
#in this case, it's all numbers, so no problemo
monthly = uploads.groupby(pd.Grouper(freq='M')).sum()

#if you want to sort in pandas, which I won't here
#monthly.sort_values('discoveredGps', ascending=False)

#same thing, but for daily
daily = uploads.groupby(pd.Grouper(freq='D')).sum()

#spew to csv. change path if you want a different location, otherwise wherever you ran the script
daily.to_csv('daily_upload_stats.csv', index=True)
monthly.to_csv('monthly_upload_stats.csv', index=True)



