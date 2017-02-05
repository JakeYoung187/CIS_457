#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: January 25, 2017
Purpose: CIS 457 Project 1
Details: TCP File Transfer
'''

import socket, os, sys

host = ''
port = int(raw_input('port: '))
if port < 0 or port > 65536:
	print "Invalid Port Number"
	sys.exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

# multiple clients in sequence
while 1:
	print "Waiting for file request from client..."
	conn, addr = s.accept()
	print 'Connected by', addr
	
	# receive filename from client
	filename = conn.recv(1024)
	print "File request received from client for:", repr(filename)
	
	# read this file 
	myfile = open(filename, 'r')
	myfilestr = myfile.read()
	print "File sent to client."
	
	# create a string of file length with 100-n blanks appended
	# so server knows exact length of filelength string
	myfilelen =  str(len(myfilestr))
	myblanks = ' ' * (100-len(myfilelen))
	mynewfilelen = myfilelen + myblanks
	conn.sendall(mynewfilelen)
	conn.sendall(myfilestr)
conn.close()
