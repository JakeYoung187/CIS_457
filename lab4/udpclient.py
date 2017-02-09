#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 20, 2017
Purpose: CIS 457 Lab 2
Details: TCP Echo Client/Server
'''

import socket, sys

host = raw_input('host: ')
port = int(raw_input('port: '))

quitStrs = ['quit', 'done', 'bye', 'exit']

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while 1:
	message = raw_input('\nEnter your message: ')
	if any(x in message.lower() for x in quitStrs):
		print "\nClient quitting..."
		sys.exit(-1)
	s.sendto(message, (host, port))
	data, server_addr = s.recvfrom(1024)
	print "Received echo: '{}' from {}".format(data, server_addr)
s.close()
