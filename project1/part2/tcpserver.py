#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: February 6, 2017
Purpose: CIS 457 Project 1 Part 2
Details: TCP Multi-threaded File Transfer
'''

import socket, os, sys, threading

class myThread (threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
	def run(self):
		while 1:
			filename = self.conn.recv(1024)
			if filename == "Client quitting":
				print "\n",filename
				self.conn.close()
				os._exit(1)	
			else:
				# receive filename from client
				#filename = self.conn.recv(1024)
				print "File request received from client for:", filename

				# read this file 
				myfile = open(filename, 'r')
				myfilestr = myfile.read()
				print myfilestr
				print "File sent to client."

				# create a string of file length with 100-n blanks appended
				# so server knows exact length of filelength string
				myfilelen =  str(len(myfilestr))
				myblanks = ' ' * (100-len(myfilelen))
				mynewfilelen = myfilelen + myblanks
				self.conn.sendall(mynewfilelen)
				self.conn.sendall(myfilestr)

def main():

	host = ''
	port = int(raw_input('port: '))
	if port < 0 or port > 65536:
		print "Invalid Port Number"
		sys.exit(0)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		print 'Connected by', addr
		thread = myThread(conn)
		thread.start()
		
if __name__ == "__main__":
    main()
