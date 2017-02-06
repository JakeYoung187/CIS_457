#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: February 6, 2017
Purpose: CIS 457 Project 1 Part 2
Details: TCP Multi-threaded File Transfer
'''

import socket, os, sys, threading, time

class myThread (threading.Thread):
	def __init__(self, s, filename):
		threading.Thread.__init__(self)
		self.s = s
		self.filename = filename
	
	def run(self):
		# client thread running
		#myfilename = raw_input('Enter filename to be received from server: ')
		myfilename = self.filename

		if myfilename == "Server quitting":
			print myfilename
			self.s.close()
			os._exit(1)
		else:

			# send filename to server
			self.s.sendall(myfilename)
			print "Sent filename to server."
			#'''
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
			#'''
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
		time.sleep(1)
		myfilename = raw_input('Enter filename to be received from server: ')
		if myfilename.lower() == "quit":
			s.sendall("Client quitting")
			s.close()
			os._exit(1)
		else:
			thread = myThread(s, myfilename)
			thread.start()
	#		print "starting thread"

if __name__ == "__main__":
    main()
