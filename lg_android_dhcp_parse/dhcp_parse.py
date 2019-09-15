#!/usr/bin/env python
import sys
import os
import csv
from binascii import hexlify
from datetime import timedelta, datetime


'''this parses dhcp assignments in android devices, which store the ip address assignment
as-is, just as the dhcp ack packet is received, so it follows the exact structure of the dhcp
ack packet. I found most of this on the wikipedia article on dhcp'''


def ip_addr(addr):
	'''this just converts each ip address from hex to regular (192.168.1.10 format
	and will return NA if any given ip address is 0.0.0.0, which is quite common for
	anything but the "your ip" or assigned ip'''
	
	if len(addr) % 2: #modular division
		print "Must be an even number of characters."
		return 'Invalid IP'
	else:
		ip_addr = ".".join([str(int(addr[x:x+2], 16)) for x in range(0,8,2)])
		if ip_addr == '0.0.0.0':
			return 'NA'
		else:
			return ip_addr

def mac_format(mac):
	'''put in colons in the client's mac address, because they are stored
	as raw hex'''
	
	formatted_mac = ":".join([mac[x:x+2] for x in range(0,12,2)])
	return formatted_mac

	
def dhcp_options(block):
	'''there are many options and they don't always show up at all or in the same order, so...
	this will parse them as they show up. It just reads the code, then the number of bytes, moving
	a pointer as it goes. It adds them to a list, then parses them. Can't work with fixed
	offsets, since every phone does it differently. I got these from the wikipedia article.'''
	
	pointer = 0
	options = []
	opt_dict = {}
	
	#set defaults for when the packet doesn't have any particular thing
	netmask = "NA"
	router = "NA"
	dns_servs = ["NA"]
	domain_name = "NA"
	lease_time = "NA"
	ack = "NA"
	dhcp_server = "NA"
	renew_time_1 = "NA"
	renew_time_2 = "NA"
	
	while pointer < len(block):
		#read specific options
		current_option = hexlify(block[pointer])
		value_bytes = int(hexlify(block[pointer + 1]), 16)
		pointer += 2
		value = hexlify(block[pointer: pointer + value_bytes])
		options.append((current_option, value))
		pointer += value_bytes

	for option in options:
		#NETMASK
		if option[0] == '01':
			netmask = ip_addr(option[1])
		
		#ROUTER/GATEWAY ADDRESS
		if option[0] == '03':
			router = ip_addr(option[1])
		
		#DNS SERVERS (can be more than 1)
		if option[0] == '06':
			dns_servs = []
			num_dns = len(option[1]) / 8
			for x in range(num_dns):
				dns_servs.append(ip_addr(option[1][x * 8: x * 8 + 8]))
			dns_servs = ' - '.join([x for x in dns_servs])
			
		#DOMAIN NAME if present
		if option[0] == '0f':
			domain_name = option[1].decode('hex').replace('\x00', '')
		
		#LEASE TIME (common is one day (86400 secs) for home networks much less for captive portals
		if option[0] == '33':
			lease_time = str(timedelta(seconds = int(option[1], 16)))

		#DHCP ACK or not (this will always be in the positive
		if option[0] == '35':
			if option[1] == '05':
				ack = 'DHCP ACK'

			else:
				ack = 'DHCP NAK'
		
		#DHCP SERVER
		if option[0] == '36':
			dhcp_server = ip_addr(option[1])
		
		#RENEW TIMES
		if option[0] == '3a':
			renew_time_1 = str(timedelta(seconds = int(option[1], 16)))
			
		if option[0] == '3b':
			renew_time_2 = str(timedelta(seconds = int(option[1], 16)))
			
	parsed_options = [ack, dhcp_server, router, dns_servs, domain_name, netmask, lease_time, renew_time_1, renew_time_2]
	return parsed_options
			
def dhcp_ack(packet):
	'''I got these offsets from the wikipedia article on dhcp
	You will have to add a timestamp if you're using the function directly'''
	
	#these things have fixed offsets - the options above do not
	xid = hexlify(packet[4:8])
	client_ip = ip_addr(hexlify(packet[12:16]))
	your_ip = ip_addr(hexlify(packet[16:20]))
	server_ip = ip_addr(hexlify(packet[20:24]))
	gateway_ip = ip_addr(hexlify(packet[24:28]))
	client_mac = mac_format(hexlify(packet[28:34]))
	magic_cookie = hexlify(packet[236:240])
	
	#the options block can have things in whatever order it chooses
	#so they'll be parsed in the dhcp_options function
	block = packet[240:]
	
	dhcp_parsed = [xid, client_ip, your_ip, server_ip, gateway_ip, client_mac, magic_cookie]
	
	#calling the options function, because... you know... options...
	dhcp_parsed.extend(dhcp_options(block))
	return dhcp_parsed
		
if __name__ == '__main__':
	results = []
	basepath = './dhcpack/'
	for file in os.listdir(basepath):
		if file.endswith('lease') or file.endswith('lease2'): #different phones have different extensions... adjust if necessary
		
			#open file, read in contents, get timestamp from file modified time
			in_file = open(basepath + file, 'rb')
			packet = in_file.read()
			ts_utc = datetime.fromtimestamp(int(os.path.getmtime(in_file.name))).strftime('%Y-%m-%d %H:%M:%S')
			in_file.close()
			
			#parse file and then insert timestamp as first element
			get_result = dhcp_ack(packet)
			get_result.insert(0, ts_utc)


			results.append(get_result)
	results.sort()
			
	#write to csv file
	out_file = open('dhcp_ack_list.csv', 'wb')
	writer = csv.writer(out_file)
	header_row = ('timestamp', 'xid', 'client_ip', 'assigned_ip', 'server_ip', 'gateway_ip', 'client_mac',\
					'magic_cookie', 'message_type', 'dhcp_server', 'router', 'dns_servers', 'domain_name', \
					'netmask', 'lease_time', 'renew_time_1', 'renew_time_2')
	writer.writerow(header_row)
	for entry in results:
		writer.writerow(entry)
	out_file.close()
