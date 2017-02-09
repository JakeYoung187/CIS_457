#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 20, 2017
Purpose: CIS 457 Lab 2
Details: TCP Echo Client/Server
'''
import socket

host = ''
port = int(raw_input('port: '))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

while 1:
	data, client_addr = s.recvfrom(1024)
	print "\nReceived message: {}".format(data)
	s.sendto(data, client_addr)
	print "Echoed back to {}".format(client_addr)
s.close()
