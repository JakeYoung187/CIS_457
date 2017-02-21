#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Client program
'''
import socket, os, sys, re

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

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while 1:
		message = raw_input('\nEnter your message: ')
		if any(x in message.lower() for x in quitStrs):
			print "\nClient quitting..."
			sys.exit(-1)
		s.sendto(message, (host, port))
		data, server_addr = s.recvfrom(1024)
		print "Received echo: '{}' from {}".format(data, server_addr)
	s.close()

if __name__ == "__main__":
    main()

