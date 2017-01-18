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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
while 1:
	data = conn.recv(1024)
	#if not data: break
	conn.sendall(data)
conn.close()
