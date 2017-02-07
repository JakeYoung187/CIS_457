#!/usr/bin/python

'''
Developer: Ellysa Stanton, Adam Terwilliger
Version: February 6, 2017
Purpose: CIS 457 Project 1 Part 2
Details: TCP Multi-threaded File Transfer
'''

import socket, os, sys, threading

clientcount = 0

class myThread (threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
		self.serverfl = os.listdir(".")
	def run(self):
		global clientcount
		while 1:
			filename = self.conn.recv(1024)
			if filename == "Client quitting.":
				print("\nClient {} quitting".format(clientcount))
				clientcount -= 1
				if (clientcount == 0):
					print "\nServer quitting."
					self.conn.close()
					os._exit(1)	

			elif filename == "ls":
				print("\nClient {} requested a list of files on server.".format(clientcount))
				self.conn.sendall(str(self.serverfl))
			
			elif filename not in self.serverfl:
				print("\nClient {} requested a file not on server.".format(clientcount))
				myInvalidMsg = appendBlanks("File N/A",20)
				self.conn.sendall(myInvalidMsg)
			
			elif filename != '':
				# receive filename from client
				print "\nFile request received from client for:", filename

				# read this file 
				myfile = open(filename, 'r')
				myfilestr = myfile.read()
				#print "\nFile sent to client."

				# create a string of file length with 20-n blanks appended
				# so server knows exact length of filelength string
				myfilelen =  str(len(myfilestr))
				#myblanks = ' ' * (20-len(myfilelen))
				#mynewfilelen = myfilelen + myblanks
				mynewfilelen = appendBlanks(myfilelen,20)
				self.conn.sendall(mynewfilelen)
				self.conn.sendall(myfilestr)

def appendBlanks(myStr, myLen):
	myBlanks = ' ' * (myLen-len(myStr))
	return myStr + myBlanks

def main():

	host = ''
	port = -1
	
	port = raw_input('port: ')
	while not port.isdigit() or int(port) < 0 or int(port) > 65536:
		print "Invalid Port Number, try again."
		port = raw_input('port: ')

	port = int(port)

	print "Waiting for client(s) to connect."
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))

	global clientcount
	
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		print 'Connected by', addr
		clientcount += 1	
		thread = myThread(conn)
		thread.start()

if __name__ == "__main__":
    main()
