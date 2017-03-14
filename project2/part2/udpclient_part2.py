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
		#self.socket.settimeout(5)
		self.filename = ''
		self.packetSize = 64
		self.fileStr = ''

	class filePacket(object):
		def __init__(self, index=None, data=None, last=None):
			self.index = index
			self.data = data
			self.last = last
		
		def __str__(self):
			return "Size: {}\n Index: {}\n Last: {}\n Data:\n {}".format(self.size, self.index, self.last, self.data)

		def __repr__(self):
			return str(self)


	def requestFile(self):
		self.filename = raw_input('\nEnter filename to be received from server: ')
		if self.filename.lower() == "quit":
			s.close()	
			sys.exit(-1)
			
		self.socket.sendto(self.filename, self.server_addr)

	def parsePacket(self, packetStr):
		myPacket = self.filePacket()
		packetHeader = packetStr.split("\n")
		myPacket.index = int(packetHeader[0].split(":")[1])
		myPacket.last = int(packetHeader[1].split(":")[1])
		myPacket.data = packetStr[packetStr.index('ENDOFHEADER') + len('ENDOFHEADER'):]

		return myPacket		

	def receiveFilePackets(self):

		while 1:
			try:
				time.sleep(1)	
				raw_packet, self.server_addr = self.socket.recvfrom(self.packetSize)
				curr_packet = self.parsePacket(raw_packet)
				print "Received packet {}".format(str(curr_packet.index))
				self.socket.sendto(str(curr_packet.index), self.server_addr)
				print "Sent acknowledgement for packet {}".format(str(curr_packet.index))
				self.fileStr += curr_packet.data
			#except self.timeout:
			#	print "Timeout error"
			except KeyboardInterrupt:
				print self.fileStr
				sys.exit(-1)

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

	print "hi client"

if __name__ == "__main__":
	main(sys.argv)
