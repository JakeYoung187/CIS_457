#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: January 25, 2017
Purpose: CIS 457 Project 1
Details: TCP File Transfer
'''

import socket
import os

host = ''
port = int(raw_input('port: '))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

while 1:
	conn, addr = s.accept()
	print 'Connected by', addr
	data = conn.recv(1024)
	#print "Received from client:", repr(data)
	#filename = repr(data)
	filename = data
	myfile = open(filename, 'r')
	myfilestr = myfile.read()
	print "Loading file...", myfilestr
	#print os.path.getsize(data)
	myfilelen =  str(len(myfilestr))
	myblanks = ' ' * (100-len(myfilelen))
	mynewfilelen = myfilelen + myblanks
	conn.send(mynewfilelen)
	conn.sendall(myfilestr)
conn.close()
