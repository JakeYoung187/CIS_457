#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Client program
'''
import socket, os, sys, re, time
class filePacket(object):
	def __init__(self, size=None, index=None, data=None, last=None):
		self.size = size
		self.index = index
		self.data = data
		self.last = last
		self.ackSent = 0
	def __str__(self):
		return "Size: {}\n Index: {}\n Last: {}\n Data:\n {}".format(self.size, self.index, self.last, self.data)

	def __repr__(self):
		return str(self)

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

def main(argv):
	
	# either enter host/port by command line or user input
	if len(argv) == 3:
		host = argv[1]
		port = int(argv[2])
	
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

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	s.settimeout(3.0)

	# only one file for now
	#while 1:
	myfilename = raw_input('\nEnter filename to be received from server: ')
	if myfilename.lower() == "quit":
		s.close()	
		sys.exit(-1)
		
	s.sendto(myfilename, (host, port))
	packetList = []
	
	testVar = 0

	while 1:
		try:
			packetStr, server_addr = s.recvfrom(69)
			x = filePacket()
			packetHeader = packetStr.split("\n")
			x.size = int(packetHeader[0].split(":")[1])	
			x.index = int(packetHeader[1].split(":")[1])	
			x.last = int(packetHeader[2].split(":")[1])	
			x.data = packetStr[packetStr.index('ENDOFHEADER') + len('ENDOFHEADER'):]
			
			testVar +=1

			packetList.append(x)
			print "Received packet {}".format(str(x.index))

			s.sendto(str(x.index), (host, port)) 
			print "Sending acknowledgement to server for packet {}".format(str(x.index))

			# exit while when get last packet
			if x.last:
				break
		except:
			print "Timeout error"
			#sys.exit(-1)

	fullFileStr = ''
	for packet in packetList:
		fullFileStr += packet.data

	mynewfile = open('new_' + myfilename, 'w')
	mynewfile.write(fullFileStr)
	print("\nFile written as: 'new_{}'".format(myfilename))

	s.close()

if __name__ == "__main__":
	main(sys.argv)

