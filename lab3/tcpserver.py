#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 27, 2017
Purpose: CIS 457 Lab 3
Details: TCP Simple Chat
'''

import socket, os, sys, threading

class myThread (threading.Thread):
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.conn = conn
	def run(self):
		# server thread running
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
	s.listen(1)
	conn, addr = s.accept()
	print 'Connected by', addr
	
	while 1:
		thread = myThread(conn)
		#thread.setDaemon(True)
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
