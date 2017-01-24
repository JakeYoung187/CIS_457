#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: January 25, 2017
Purpose: CIS 457 Project 1
Details: TCP File Transfer
'''

import socket

host = raw_input('host: ')
port = int(raw_input('port: '))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
myfilename = raw_input('Enter filename to be received: ')
s.sendall(myfilename)
myfilelen = s.recv(100)
myfilelen = int(myfilelen.strip())
myfilestr = s.recv(myfilelen)
mynewfile = open("new_" + myfilename, 'w')
mynewfile.write(myfilestr)
s.close()
