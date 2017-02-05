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
		new_message = self.conn.recv(1024)
		if new_message == "Client quitting":
			print "\n",new_message
			self.conn.close()
			os._exit(1)	
		else:
			print "\nClient:",new_message
			print "\nServer: "

def main():

	host = ''
	port = int(raw_input('port: '))
	if port < 0 or port > 65536:
		print "Invalid Port Number"
		sys.exit(0)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	#s.listen(1)
	
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		print 'Connected by', addr
		thread = myThread(conn)
		thread.start()
		
		message = raw_input('\nServer: ')
		
		if message.lower() == "quit":
			conn.sendall("Server quitting")
			conn.close()
			os._exit(1)

		else:
			conn.sendall(message)

if __name__ == "__main__":
    main()
