#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: March 21, 2017
Purpose: CIS 457 Project 3 Part 1
         Virtual Router
Details: Implementing a simplified version of a router in software
         in order to learn about the function of a router.
'''

import socket, os, sys
import netifaces
from struct import *

def main(argv):    
    #print netifaces.interfaces()
    #print netifaces.ifaddresses('lo')
    #print netifaces.ifaddresses('r1-eth0')

    try: 
        #s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x003))
        print "Socket created correctly."
        print s
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit(-1)
    
    while 1:
        print "In While Loop!"
        raw_packet, host_addr = s.recvfrom(2048)
        print raw_packet
        
        

if __name__ == "__main__":
    main(sys.argv)
