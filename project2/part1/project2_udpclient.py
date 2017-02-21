#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Client program
'''
import socket, os, sys, re
class filePacket(object):
	def __init__(self, size=None, index=None, data=None, last=None):
		self.size = size
		self.index = index
		self.data = data
		self.last = last
		self.ackSent = 0
	def __str__(self):
		return "Size: {}\n Index: {}\n Last: {}\n Data: {}".format(self.size, self.index, self.last, self.data)

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
	# only one file for now
	#while 1:
	myfilename = raw_input('\nEnter filename to be received from server: ')
	if myfilename.lower() == "quit":
		s.close()	
		sys.exit(-1)
	else:
		s.sendto(myfilename, (host, port))
		packetList = []
		while 1:
			packetStr, server_addr = s.recvfrom(1024)
			print packetStr, "\n\n"
			x = filePacket()
			for line in packetStr.split("\n"):
				classVar = line.split(":")[0]
				classVal = line.split(":")[1]
				# could probably clean up with switch/cases
				if classVar == "Size":
					x.size = classVal
				elif classVar == "Index":
					x.index = classVal
				elif classVar == "Last":
					x.last = classVal
				elif classVar == "Data":
					x.data = classVal

			packetList.append(x)
		
			if x.last:
				break

		for packet in packetList:
			print packet

	s.close()

if __name__ == "__main__":
	main(sys.argv)

