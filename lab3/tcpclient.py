#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 27, 2017
Purpose: CIS 457 Lab 3
Details: TCP Simple Chat
'''

import socket, sys

host = raw_input('host: ')
if host != "127.0.0.1":
	print "Non loopback host"
	sys.exit(0)

port = int(raw_input('port: '))
if port < 0 or port > 65536:
    print "Invalid Port Number"
    sys.exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

message = raw_input('Enter message: ')

s.sendall(message)

new_message = s.recv(1024)

print new_message

s.close()
