#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Server program
'''
import socket, os, sys, re

def main():
	
	host = ''
	port = raw_input('port: ')

	# check for non-characters and negative or large port numbers
	while not port.isdigit() or int(port) < 0 or int(port) > 65536:
		print "Invalid Port Number, try again."
		port = raw_input('port: ')

	# cast port only when know it's valid
	port = int(port)
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, port))

	while 1:
		data, client_addr = s.recvfrom(1024)
		print "\nReceived message: {}".format(data)
		s.sendto(data, client_addr)
		print "Echoed back to {}".format(client_addr)
	s.close()

if __name__ == "__main__":
    main()
