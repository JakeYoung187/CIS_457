#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: February 27, 2017
Purpose: CIS 457 Project 2 Part 2
Details: UDP File Transfer

Client program
'''
import socket, os, sys, math, time

class Client(object):
	def __init__(self, server_host, port):
		self.server_host = server_host
		self.port = port
		self.server_addr = (self.server_host, self.port)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.settimeout(5)
		self.filename = ''
		self.packetSize = 128
		self.fileStr = ''
		self.leftMostPacket = 0
		self.currentWindow = {}
		self.numPackets = 0

	class filePacket(object):
		def __init__(self, index=None, data=None, serverSentCS=None):
			self.index = index
			self.data = data
			self.checksum = '0x00'
			self.serverSentCS = serverSentCS
			self.clientRecvCS = '0x00'
		
		def __str__(self):
			return "Index:{}\nChecksum:{}\nENDOFHEADER{}".format(self.index, self.checksum, self.data)

		def __repr__(self):
			return str(self)


	def requestFile(self):
		self.filename = raw_input('\nEnter filename to be received from server: ')
		if self.filename.lower() == "quit":
			s.close()	
			sys.exit(-1)
		print "Sent original file request"			
		self.socket.sendto(self.filename, self.server_addr)
		while 1:
			try:
				fq_ack, self.server_addr = self.socket.recvfrom(1024)
				#if "HEADER" not in fq_ack:
				#	print "Received file request ack"
				break
			except socket.timeout:
				print "Resent file request"			
				self.socket.sendto(self.filename, self.server_addr)

	def parsePacket(self, packetStr):
		try:
			myPacket = self.filePacket()
			packetHeader = packetStr.split("\n")
			myPacket.index = int(packetHeader[0].split(":")[1])
			myPacket.serverSentCS = packetHeader[1].split(":")[1]
			myPacket.data = packetStr[packetStr.index('ENDOFHEADER') + len('ENDOFHEADER'):]
		except:
			myPacket.data = 'Corrupted'

		return myPacket		

	def getCheckSum(self, myStr):

		binPacketList = map(bin, bytearray(str(myStr)))

		result = 0
		for binByte in binPacketList:
			intBinByte = int(binByte, 2)
			result += intBinByte
			binResult = bin(result)
			if len(binResult) == 11:
				result -= 256
				result += 1

		binResult = bin(result)[2:]
		while(len(binResult) < 8):
			binResult = ('0' + binResult)

		onesComp = ''
		for bit in binResult:
			if bit == '0':
				onesComp += '1'
			elif bit == '1':
				onesComp += '0'

		finalByte = int(onesComp, 2)
		hexValue = hex(finalByte)

		return hexValue

	# compare checksums for corruption
	# equivalent to result all 1s
	def checkCorruption(self, packet):

		packet.clientRecvCS = self.getCheckSum(str(packet))
	
		corr = False
		try:
			if int(packet.serverSentCS, 16) - int(packet.clientRecvCS, 16) != 0:
				corr = True
		except:
			corr = True	
	
		return corr

	# write currentWindow out to M
	def writeFile(self):
		fullFileStr = ''
		for i in range(self.numPackets):
			fullFileStr += self.currentWindow[i].data
		
		mynewfile = open('new_' + self.filename, 'w')
		mynewfile.write(fullFileStr)
		print("File written as: 'new_{}'".format(self.filename))	

	def receiveFilePackets(self):
		
		self.socket.settimeout(10)

		while 1:
			try:
				raw_packet, self.server_addr = self.socket.recvfrom(self.packetSize)
				
				if "all done" in raw_packet:
					print "\nNo more packets from server..."
					self.writeFile()
					break

				# receiving data, not file request
				if "request" not in raw_packet:
					curr_packet = self.parsePacket(raw_packet)
					print "Received packet {}".format(str(curr_packet.index))

					if curr_packet.data == 'Corrupted' or self.checkCorruption(curr_packet):
						print "Corruption in packet {}, no ack sent".format(str(curr_packet.index))	
						print "Server sent checksum: {}, Client received checksum: {}".format(
							curr_packet.serverSentCS, curr_packet.clientRecvCS)
					else:
						if curr_packet.index not in self.currentWindow:
							self.currentWindow[curr_packet.index] = curr_packet
							self.numPackets += 1
						ackIndex = str(curr_packet.index)
						ackCS = self.getCheckSum(ackIndex)
						ackToSend = ackIndex + ":" + str(ackCS)
						self.socket.sendto(ackToSend, self.server_addr)
						print "Sent acknowledgment for packet {}".format(ackIndex)
					
			except socket.timeout:
				#print "\nNo more packets from server..."
				#self.writeFile()
				#break
				print "Socket timeout...server is taking awhile..."			

			except KeyboardInterrupt:
				print "Come back again soon..."
				break

#Regular Expression check for valid host name
#http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def is_valid_hostname(hostname):
	if len(hostname) > 255:
		return False
	if hostname[-1] == ".":
		# strip exactly one dot from the right, if present
		hostname = hostname[:-1]
	allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
	return all(allowed.match(x) for x in hostname.split("."))

def getHostAndPort(argsFromCommandLine):
	
	# either enter host/port by command line or user input
	if len(argsFromCommandLine) == 3:
		host = argsFromCommandLine[1]
		port = int(argsFromCommandLine[2])
	
	else:
		host = raw_input('host: ')

		# use regular expression function
		while not is_valid_hostname(host):
			print "Invalid host, try again."
			host = raw_input('host: ')

		port = raw_input('port: ')

		# check for non-characters and negative or large port numbers
		while not port.isdigit() or int(port) < 0 or int(port) > 65536:
			print "Invalid Port Number, try again."
		port = raw_input('port: ')

		# cast port only when know it's valid
		port = int(port)

	return host, port

def main(argv):
	
	host, port = getHostAndPort(argv)

	c = Client(host, port)

	c.requestFile()

	c.receiveFilePackets()

	print "Goodbye from client!"

if __name__ == "__main__":
	main(sys.argv)
