#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: January 25, 2017
Purpose: CIS 457 Project 1
Details: TCP File Transfer
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

myfilename = raw_input('Enter filename to be received from server: ')

# send filename to server
s.sendall(myfilename)

# receive filelength as string from server
myfilelen = s.recv(100)
myfilelen = int(myfilelen.strip())

# receive file as one string from server
myfilestr = s.recv(myfilelen)
print "Received file '" +  myfilename + "' from server"

# write file to new_filename
mynewfile = open("new_" + myfilename, 'w')
mynewfile.write(myfilestr)
print("File written as: 'new_{}".format(myfilename))
s.close()
