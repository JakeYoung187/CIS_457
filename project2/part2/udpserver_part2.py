#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: March 15, 2017
Purpose: CIS 457 Project 2 Part 2
		 UDP Reliability File Transfer
Details: Areas of relability include:
		  - Loss
		  - Duplication
		  - Reordering
		  - Corruption

Server program
'''
import socket, os, sys, math, time

'''
Server class is a UDP socket with numerous fields
that help to implement a reliable file transfer
using the sliding window protocol. 
'''
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
	
	'''
    filePacket class is an object that is 
    transferred between server and client.
    '''
	class filePacket(object):
		def __init__(self, index, data, checksum):
			self.index = index
			self.data = data
			self.checksum = checksum
			self.ackRecv = 0

		def __str__(self):
			return "Index:{}\nChecksum:{}\nENDOFHEADER{}".format(self.index, self.checksum, self.data)

		def __repr__(self):
			return str(self)	

	'''
	getFilename method receives file request from client and 
		verifies the file exists in its local directory
	'''
	def getFilename(self):
		
		print "Waiting for client to request a file..."	
		while 1:
			try:
				self.filename, self.client_addr = self.socket.recvfrom(1024)
				if self.filename in os.listdir("."):
					print ("\nSent ack for request of file: {}".format(self.filename))
					self.socket.sendto("File request received", self.client_addr)
					self.fileSize = os.path.getsize(self.filename)
					self.setNumberOfPackets()
					break
				else:
					self.filename = ''
			except socket.timeout:
				print "Socket timeout...please request a file."
			except KeyboardInterrupt:
				print "\nCome again soon..."
				sys.exit(-1)

	'''
	setNumberOfPackets is a helper method to better iterate
		over the file in chunks
	'''
	def setNumberOfPackets(self):
		self.numPackets = int(math.ceil(
			float(self.fileSize) / float(self.packetDataSize)))


	'''
    getCheckSum method is abstract take any string of bytes and
        calculate its checksum
    '''
	def getCheckSum(self, myStr):

		# create a list of binary strings from bytes
		binPacketList = map(bin, bytearray(myStr))
		
		# sum all of the binary numbers in list
		result = 0
		for binByte in binPacketList:
			intBinByte = int(binByte, 2)
			result += intBinByte
			binResult = bin(result)
			if len(binResult) == 11:
				result -= 256
				result += 1

		# add leading zeroes to binary num
		binResult = bin(result)[2:]
		while(len(binResult) < 8):
			binResult = ('0' + binResult)
		
		# take one's complement
		onesComp = ''
		for bit in binResult:
			if bit == '0':
				onesComp += '1'
			elif bit == '1':
				onesComp += '0'

		# convert to binary and then hex
		finalByte = int(onesComp, 2)
		hexValue = hex(finalByte)		

		return hexValue
	
	'''
	sendPackets is the main method that is called after
		acknowledgment period has passed and the window
		has been moved
	'''
	def sendPackets(self, myfile):

		for i in range(self.leftMostPacket, self.leftMostPacket+self.windowSize):
			# don't go beyond the number of total packets
			if i <= self.numPackets:
				# if we haven't already read this fileChunk
				if i not in self.currentWindow:
					myfile.seek(i*self.packetDataSize)
					fileChunk = myfile.read(self.packetDataSize)
					curr_packet = self.filePacket(i, fileChunk, '0x00')
					#print curr_packet	
					csHex = self.getCheckSum(str(curr_packet))
					curr_packet.checksum = str(csHex)
					#print curr_packet	
					self.currentWindow[i] = curr_packet
						
				# else don't re-read file and its already in M
				else:
					curr_packet = self.currentWindow[i]		
	

				# if we haven't already received an ack for this packet
				if curr_packet.ackRecv == 0:
					print "Sending packet {}".format(curr_packet.index)
					self.socket.sendto(str(curr_packet), self.client_addr)
	
	'''
	checkForAckCorruption looks at checksums in the acknowledgement
		from the client to the server that it received a packet
	'''
	def checkForAckCorruption(self, myStr, myCS):
		try:
			myAckCS = int(self.getCheckSum(myStr), 16)
			myBinCS = int(myCS, 16)
		
			ackCor = False
			# difference between checksums should be 0
			if (myAckCS - myBinCS) != 0:
				ackCor = True
		except:
			ackCor = True

		return ackCor
	
	'''
	getAcks method loops for a set amount of time
		giving the client a chance to acknowledge
		any packets it received, while also checking
		for any possible corruption
	'''
	def getAcks(self):
		# wait for acks for n sec
		# need short time for large files (jpgs)
		#self.socket.settimeout(0.001)
		# need longer time for reorder delay
		self.socket.settimeout(5)
		while 1:
			try:
				ack, addr = self.socket.recvfrom(10)
				if ":" not in ack:
					print "Acknowledgment for unknown packet was corrupted..."
					break
				elif ":" in ack:
					ackParts = ack.split(":")
					ackIndex = ackParts[0]
					ackCS = ackParts[1]

					if not ackIndex.isdigit():
						print "Acknowledgment for unknown packet was corrupted..."
						break
						
					elif ackIndex.isdigit():
						# check for corruption and don't add to ack recv
						if self.checkForAckCorruption(str(ackIndex), ackCS):
							print "Acknowledgment for packet {} was corrupted...".format(ackIndex)
							break				
						else:
							print "Received acknowledgment for packet {}".format(ackIndex)
							self.currentWindow[int(ackIndex)].ackRecv = 1		
							time.sleep(0.0001)
								
			except socket.timeout:
				#print "Ack timeout"
				break
			except KeyboardInterrupt:
				print "\nCome again soon..."
				sys.exit(-1)
	
	'''
	slideWindow utilizes the leftMostPacket acknowledged
		to figure out how far to slide the window
	'''
	def slideWindow(self):

		slideSize = 0
		while slideSize < self.windowSize and self.leftMostPacket <= self.numPackets:
			if self.currentWindow[self.leftMostPacket].ackRecv == 0:
				break
			else:
				self.leftMostPacket += 1
				self.numAcksRecv +=1
				slideSize +=1

	'''
	serveFileRequests is the main method that brings
		together all of the other methods in the Server
		class to send packets and get acknowledgments 
		from the client
	'''
	def serveFileRequests(self):	

		# file pointer to requested file
		fp = open(self.filename, 'r')

		# send entire initial window
		self.sendPackets(fp)

		# loop until we've received
		# num unique acks = num packets
		while 1:
			self.getAcks()
			self.slideWindow()
			if self.numAcksRecv >= self.numPackets:
				print "\nAll acks received from client..."
				self.socket.sendto("Hooray, we're all done!", self.client_addr)
				break
			else:
				self.sendPackets(fp)

'''
getPort is a helper method for error handling of raw input for port nums
'''	
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
