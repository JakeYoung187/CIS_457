#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: January 27, 2017
Purpose: CIS 457 Lab 3
Details: TCP Simple Chat
'''

import socket, os, sys, threading

class myThread (threading.Thread):
	def __init__(self, s):
		threading.Thread.__init__(self)
		self.s = s
	
	def run(self):
		# client thread running
		new_message = self.s.recv(1024)
		if new_message == "Server quitting":
			print "\n",new_message
			self.s.close()
			os._exit(1)
		else:
			print "\nServer:",new_message
			print "\nClient: "


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
		
		message = raw_input('\nClient: ')
		
		if message.lower() == "quit":
			s.sendall("Client quitting")
			s.close()
			os._exit(1)
	
		else:
			s.sendall(message)

if __name__ == "__main__":
    main()
