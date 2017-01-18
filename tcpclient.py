#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 20, 2017
Purpose: CIS 457 Lab 2
Details: TCP Echo Client/Server
'''

import socket

#host = '127.0.0.1'
#port = 9876
host = raw_input('host: ')
port = int(raw_input('port: '))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
#s.sendall('Hello, world')
message = raw_input('Enter your message: ')
s.sendall(message)
data = s.recv(1024)
s.close()
print 'Received', repr(data)
