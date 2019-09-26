#!/usr/bin/env python3

'''just a simple script to pull the latest oui.csv from the IEEE
and write it to a sqlite db with the date as the filename'''

import sqlite3
import csv
import datetime
import codecs
from urllib.request import urlopen

#get current utc time
time_now = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

#create database, named with current utc time
con = sqlite3.connect('{}_macvendors.db'.format(time_now))
cur = con.cursor()
cur.execute('CREATE TABLE macvendors(mac TEXT, vendor TEXT, vendor_address TEXT);')

#get the current file
url = 'https://standards.ieee.org/develop/regauth/oui/oui.csv'

#get the file and set up csv reader
response = urlopen(url)
reader = csv.reader(codecs.iterdecode(response, 'utf-8'))

#read file data and insert into db
next(reader) #skip header row
for line in reader:
	entry = line[1:] #this skips the first entry of each line
	cur.executemany('INSERT INTO macvendors VALUES (?, ?, ?);', (entry,))
	
con.commit()
con.close()