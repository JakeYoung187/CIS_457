#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: February 27, 2017
Purpose: CIS 457 Project 2 Part 2
Details: UDP File Transfer

Server program
'''
import socket, os, sys, math, time


class Server(object):
	def __init__(self, port):
		self.port = port
		self.client_addr = None
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(('',self.port))
		self.socket.settimeout(10)
		self.filename = ''
		self.windowSize = 10
		self.packetDataSize = 32
		self.fileSize = 0
		self.numPackets = 0
		self.currentWindow = []	
	
	class filePacket(object):
		def __init__(self, index, data, last):
			self.index = index
			self.data = data
			self.last = last

		def __str__(self):
			return "Index:{}\nLast:{}\nENDOFHEADER{}".format(self.index, self.last, self.data)

		def __repr__(self):
			return str(self)	


	def getFilename(self):
		
		print "Waiting for client(s) to request a file..."	
		self.filename, self.client_addr = self.socket.recvfrom(1024)

		if self.filename in os.listdir("."):
			print ("\nFile request received from client for: {}".format(self.filename))
	
			self.fileSize = os.path.getsize(self.filename)
			self.setNumberOfPackets()

	def serveFileRequests(self):	

		with open(self.filename, 'r') as myfile:

			for i in range(self.windowSize):
				fileChunk = myfile.read(self.packetDataSize)
				curr_packet = self.filePacket(i, fileChunk, 0)
				self.currentWindow.append(curr_packet)
			
			#print self.currentWindow

			#for packet in self.currentWindow:
			#if True:
				#if packet.index == 3:
				
				#print "\nPacket contents:\n", curr_packet
				print "Sending packet {} of size {}".format(curr_packet.index, len(str(curr_packet)))
				self.socket.sendto(str(curr_packet), self.client_addr)
				
				time.sleep(1)

				ack, addr = self.socket.recvfrom(10)
				print "Received ack from {}".format(ack)
		
	def setNumberOfPackets(self):
		self.numPackets = int(math.ceil(
			float(self.fileSize) / float(self.packetDataSize)))
	

def getPort(argsFromCommandLine):
	
	if len(argsFromCommandLine) == 2:
		port = int(argsFromCommandLine[1])

	else:
		port = raw_input('port: ')

		# check for non-characters and negative or large port numbers
		while not port.isdigit() or int(port) < 0 or int(port) > 65536:
			print "Invalid Port Number, try again."
			port = raw_input('port: ')

		# cast port only when know it's valid
		port = int(port)

	return port

def main(argv):

	port = getPort(argv)

	s = Server(port)

	s.getFilename()

	s.serveFileRequests()

	print "hi server"

if __name__ == "__main__":
    main(sys.argv)
