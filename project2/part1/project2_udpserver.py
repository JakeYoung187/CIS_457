#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Server program
'''
import socket, os, sys

# http://stackoverflow.com/questions/15599639/whats-perfect-counterpart-in-python-for-while-not-eof
from functools import partial

class filePacket(object):
	def __init__(self, size, index, data, last):
		self.size = size
		self.index = index
		self.data = data
		self.last = last 
		self.ackRecv = 0

	def __str__(self):
		return "Size:{}\nIndex:{}\nLast:{}\nENDOFHEADER{}".format(self.size, self.index, self.last, self.data)

	def __repr__(self):
		return str(self)

def main(argv):

	host = ''

	if len(argv) == 2:
		port = int(argv[1])

	else:
		port = raw_input('port: ')

		# check for non-characters and negative or large port numbers
		while not port.isdigit() or int(port) < 0 or int(port) > 65536:
			print "Invalid Port Number, try again."
			port = raw_input('port: ')

		# cast port only when know it's valid
		port = int(port)

	print "Waiting for client(s) to request file(s)..."	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, port))

	#while 1:
	filename, client_addr = s.recvfrom(1024)
	if filename in os.listdir("."):
		
		# receive filename from client
		print ("\nFile request received from client for: {}".format(filename))
		
		# read this file
		packetDataSize = 32
		packetIndex = 0
		packetList = []
		with open(filename, 'r') as myfile:
			for fileChunk in iter(partial(myfile.read, packetDataSize), ''):
				x = filePacket(packetDataSize, packetIndex, fileChunk, 0)
				packetList.append(x)
				packetIndex+=1
		packetList[packetIndex-1].last = 1

		for packet in packetList:
			print "Sending packet {}".format(packet.index)
			print len(str(packet))
			s.sendto(str(packet), client_addr)

	s.close()

if __name__ == "__main__":
    main(sys.argv)
