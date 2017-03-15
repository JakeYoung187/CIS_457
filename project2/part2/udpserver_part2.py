#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: March 15, 2017
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
		self.windowSize = 5
		self.packetDataSize = 32
		self.fileSize = 0
		self.numPackets = 0
		self.currentWindow = {}
		self.leftMostPacket = 0
		self.numAcksRecv = 0
	
	class filePacket(object):
		def __init__(self, index, data, last):
			self.index = index
			self.data = data
			self.last = last
			self.ackRecv = 0

		def __str__(self):
			return "Index:{}\nLast:{}\nENDOFHEADER{}".format(self.index, self.last, self.data)

		def __repr__(self):
			return str(self)	

	def getFilename(self):
		
		print "Waiting for client(s) to request a file..."	
		while 1:
			try:
				self.filename, self.client_addr = self.socket.recvfrom(1024)
				if self.filename in os.listdir("."):
					print ("\nSent ack for request of file: {}".format(self.filename))
					self.socket.sendto("File request received", self.client_addr)
					self.fileSize = os.path.getsize(self.filename)
					self.setNumberOfPackets()
				break
			except socket.timeout:
				print "Socket timeout...please request a file."
			except KeyboardInterrupt:
				print "\nCome again soon..."
				sys.exit(-1)

	
	def setNumberOfPackets(self):
		self.numPackets = int(math.ceil(
			float(self.fileSize) / float(self.packetDataSize)))

	def initialServe(self, myfile):
		# send initial window
		for i in range(self.windowSize):
			fileChunk = myfile.read(self.packetDataSize)
			curr_packet = self.filePacket(i, fileChunk, 0)
			self.currentWindow[i] = curr_packet
			print "Sending packet {}".format(curr_packet.index)
			self.socket.sendto(str(curr_packet), self.client_addr)

	def nextServe(self, myfile):
		
		#print "Leftmost packet: {}".format(self.leftMostPacket)

		for i in range(self.leftMostPacket, self.leftMostPacket+self.windowSize):
			# if we haven't already read this fileChunk
			if i <= self.numPackets:
				if i not in self.currentWindow:
					myfile.seek(i*self.packetDataSize)
					fileChunk = myfile.read(self.packetDataSize)
					curr_packet = self.filePacket(i, fileChunk, 0)
					if i == self.numPackets:
						curr_packet.last = 1
					self.currentWindow[i] = curr_packet
						
				else:
					curr_packet = self.currentWindow[i]		
		
				print "Sending packet {}".format(curr_packet.index)
				self.socket.sendto(str(curr_packet), self.client_addr)
			
	def getAcks(self):
		# wait for acks for n sec
		# need short time for large files (jpgs)
		self.socket.settimeout(0.001)
		# need longer time for reorder delay
		#self.socket.settimeout(3)
		while 1:
			try:
				ack, addr = self.socket.recvfrom(10)
				print "Received acknowledgment for packet {}".format(ack)
				self.currentWindow[int(ack)].ackRecv = 1		
				time.sleep(0.0001)
			except socket.timeout:
				#print "Ack timeout"
				break
			except KeyboardInterrupt:
				print "\nCome again soon..."
				sys.exit(-1)
	
	def slideWindow(self):

		slideSize = 0
		while slideSize < self.windowSize and self.leftMostPacket <= self.numPackets:
			if self.currentWindow[self.leftMostPacket].ackRecv == 0:
				break
			else:
				self.leftMostPacket += 1
				self.numAcksRecv +=1
				slideSize +=1

	def serveFileRequests(self):	

		fp = open(self.filename, 'r')
		self.initialServe(fp)
		while 1:
			self.getAcks()
			self.slideWindow()
			if self.numAcksRecv >= self.numPackets:
				break
			else:
				self.nextServe(fp)
	
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

	print "Goodbye from server!"

if __name__ == "__main__":
    main(sys.argv)
