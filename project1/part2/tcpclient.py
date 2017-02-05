#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: February 6, 2017
Purpose: CIS 457 Project 1 Part 2
Details: TCP Multi-threaded File Transfer
'''

import socket, os, sys, threading

class myThread (threading.Thread):
	def __init__(self, s):
		threading.Thread.__init__(self)
		self.s = s
	
	def run(self):
		# client thread running
		myfilename = self.s.recv(1024)
		if myfilename == "Server quitting":
			print "\n",myfilename
			self.s.close()
			os._exit(1)
		'''
		else:
			myfilename = raw_input('Enter filename to be received from server: ')

			print "Sending filename to server."

			# send filename to server
			self.s.sendall(myfilename)

			# receive filelength as string from server
			myfilelen = self.s.recv(100)
			myfilelen = int(myfilelen.strip())

			# receive file as one string from server
			myfilestr = self.s.recv(myfilelen)
			print "Received file '" +  myfilename + "' from server"

			# write file to new_filename
			mynewfile = open("new_" + myfilename, 'w')
			mynewfile.write(myfilestr)
			print("File written as: 'new_{}".format(myfilename))
		'''

def main():

	host = raw_input('host: ')
	if host != "127.0.0.1":
		print "Non loopback host"
		sys.exit(0)

	port = int(raw_input('port: '))
	if port < 0 or port > 65536:
		print "Invalid Port Number"
		sys.exit(0)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))

	while 1:
		thread = myThread(s)
		thread.start()
	
		myfilename = raw_input('Enter filename to be received from server: ')

		print "Sending filename to server."

		# send filename to server
		s.sendall(myfilename)


		# receive filelength as string from server
		myfilelen = s.recv(10)
		myfilelen = int(myfilelen.strip())

		print myfilelen

		# receive file as one string from server
		myfilestr = s.recv(myfilelen)
		print "Received file '" +  myfilename + "' from server"

		# write file to new_filename
		mynewfile = open("new_" + myfilename, 'w')
		mynewfile.write(myfilestr)
		print("File written as: 'new_{}".format(myfilename))
		
		if myfilename.lower() == "quit":
			s.sendall("Client quitting")
			s.close()
			os._exit(1)
	
		#else:
		#	s.sendall(myfilename)

if __name__ == "__main__":
    main()
