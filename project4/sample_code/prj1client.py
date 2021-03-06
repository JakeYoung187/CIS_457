#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: February 6, 2017
Purpose: CIS 457 Project 1 Part 2
Details: TCP Multi-threaded File Transfer

Client program
'''

import socket, os, sys, threading, time, re

# using Python threads for pedagogical purposes
# as due to the global interpreter lock
# Python is not truly "multi-threaded" 
class myThread (threading.Thread):

	# initialize thread class
	# pass socket and filename as parameters
	def __init__(self, s, filename):
		threading.Thread.__init__(self)
		self.s = s
		self.filename = filename
	
	# run script executes on thread.start()
	def run(self):
		
		# client always sends filename 
		self.s.sendall(self.filename)

		# either get list of files from server
		if self.filename == "ls":
			print "\nSent request for list of files in server."
			filelist = self.s.recv(1024)
			print filelist

		# or request a specific file
		else:	
			print "\nSent filename to server."
			
			# recv string with blanks added
			myfilelen = self.s.recv(100).strip()
			
			if myfilelen == "File N/A":
				print "\nInvalid file. Type \"ls\" to see available files on server."
			
			else:
				# receive filelength as string from server
				myfilelen = int(myfilelen)

				# receive file as one string from server
				myfilestr = self.s.recv(myfilelen)
				print "\nReceived file '" +  self.filename + "' from server"

				# write file to new_filename
				mynewfile = open("new_" + self.filename, 'w')
				mynewfile.write(myfilestr)
				print("\nFile written as: 'new_{}".format(self.filename))

#Regular Expression check for valid host name
#http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def is_valid_hostname(hostname):
	if len(hostname) > 255:
		return False
	if hostname[-1] == ".":
		hostname = hostname[:-1] # strip exactly one dot from the right, if present
	allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
	return all(allowed.match(x) for x in hostname.split("."))


def main():
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

	# intialize socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))

	# client can request multiple files
	while 1:
		time.sleep(0.1)
		myfilename = raw_input('\nEnter filename to be received from server: ')
		if myfilename.lower() == "quit":
			s.sendall("Client quitting.")
			s.close()
			os._exit(1)
		else:
			thread = myThread(s, myfilename)
			thread.start()

if __name__ == "__main__":
    main()
