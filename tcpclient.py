#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 20, 2017
Purpose: CIS 457 Lab 2
Details: TCP Echo Client/Server
'''

import socket

host = raw_input('host: ')
port = int(raw_input('port: '))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
message = raw_input('Enter your message: ')
s.sendall(message)
data = s.recv(1024)
print 'Received from server:', repr(data)
s.close()
