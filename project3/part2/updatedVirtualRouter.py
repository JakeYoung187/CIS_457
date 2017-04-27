#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: April 5, 2017
Purpose: CIS 457 Project 3 - Virtual Router
Details: Implementing a simplified version of a router in software
         in order to learn about the function of a router.
'''

import socket, os, sys, netifaces, struct, binascii, time

from copy import deepcopy


class virtualRouter(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_PACKET,socket.SOCK_RAW, 
                        socket.htons(0x003))
        self.maxPacketSize = 1024
        
    class filePacket(object):
        def __init__(self, packetBytes, ethHeader=None, arpHeader=None,
                        ipHeader=None, icmpHeader=None):
            self.netList = netifaces.interfaces()
            self.packetBytes = packetBytes
            self.packetType = 'Unknown'
        
        def displayPacket(self, inout):

            print "************************************************"    
            if inout == "in":
                print "****************_INCOMING_PACKET_***************"
            elif inout == "out":
                print "****************_OUTGOING_PACKET_***************"
            
            if self.packetType == "ARP":
                print self.ethHeader
                print self.arpHeader
            
            elif self.packetType == "ICMP":
                print self.ethHeader
                print self.ipHeader
                print self.icmpHeader
        
        def setPacketType(self):

            self.ethHeader = self.setEthHeader(self.packetBytes[0:14])

            if self.ethHeader.ethType == '\x08\x06':
                self.packetType = 'ARP'
                self.arpHeader = self.setARPHeader(self.packetBytes[14:42])
            
            else:
                self.ipHeader = self.setIPHeader(self.packetBytes[14:34])
                
                if self.ipHeader.ipType == '\x00' and self.ipHeader.ipProtocol == '\x01':
                    self.packetType = 'ICMP'
    
                    self.icmpHeader = self.setICMPHeader(self.packetBytes)
        

	class setEthHeader(object):
            def __init__(self, raw):
                self.header = struct.unpack("!6s6s2s", raw)
                self.destMAC = self.header[0]
                self.srcMAC = self.header[1]
                self.ethType = self.header[2]
            
            def getEthHeader(self):
                return (self.destMAC, self.srcMAC, self.ethType)

            def __repr__(self):
                outStr = "************************************************"
                outStr += "\n****************_ETHERNET_FRAME_****************"
                outStr += "\nDest MAC:        "+ binascii.hexlify(self.destMAC)
                outStr += "\nSource MAC:      "+ binascii.hexlify(self.srcMAC)
                outStr += "\nType:            "+ binascii.hexlify(self.ethType)
                outStr += "\n************************************************"
            
                return outStr

        class setARPHeader(object):
            def __init__(self, raw):
                self.header = struct.unpack("2s2s1s1s2s6s4s6s4s", raw)
                self.hardwareType = self.header[0]
                self.protocolType = self.header[1]
                self.hardwareSize = self.header[2]
                self.protocolSize = self.header[3]
                self.opcode = self.header[4]
                self.srcMAC = self.header[5]
                self.srcIP = self.header[6]
                self.destMAC = self.header[7]
                self.destIP = self.header[8]

            def getARPHeader(self):
                return (self.hardwareType, self.protocolType, self.hardwareSize,
                        self.protocolSize, self.opcode, self.srcMAC, self.srcIP,
                        self.destMAC, self.destIP)

            def __repr__(self):
                outStr = "******************_ARP_HEADER_******************"
                outStr += "\nHardware type:   "+ binascii.hexlify(self.hardwareType)
                outStr += "\nProtocol type:   "+ binascii.hexlify(self.protocolType)
                outStr += "\nHardware size:   "+ binascii.hexlify(self.hardwareSize)
                outStr += "\nProtocol size:   "+ binascii.hexlify(self.protocolSize)
                outStr += "\nOpcode:          "+ binascii.hexlify(self.opcode)
                outStr += "\nSource MAC:      "+ binascii.hexlify(self.srcMAC)
                outStr += "\nSource IP:       "+ socket.inet_ntoa(self.srcIP)
                outStr += "\nDest MAC:        "+ binascii.hexlify(self.destMAC)
                outStr += "\nDest IP:         "+ socket.inet_ntoa(self.destIP)
                outStr += "\n************************************************\n"

                return outStr

        class setIPHeader(object):
            def __init__(self, raw):
                self.header = struct.unpack("1s1s2s2s2s1s1s2s4s4s", raw)
                self.version = self.header[0]
                self.ipType = self.header[1]
                self.length = self.header[2]
                self.ipID = self.header[3]
                self.flags = self.header[4]
                self.ttl = self.header[5]
                self.ipProtocol = self.header[6]
                self.checksum = self.header[7]
                self.srcIP = self.header[8]
                self.destIP = self.header[9]
            
            def getIPHeader(self):
                return (self.version, self.ipType, self.length, self.ipID,
                        self.flags, self.ttl, self.ipProtocol, self.checksum,
                        self.srcIP, self.destIP)

            def __repr__(self):
                outStr = "****************_IP_HEADER_*********************"
                outStr += "\nVersion/IHL:     "+ binascii.hexlify(self.version)
                outStr += "\nType of service: "+ binascii.hexlify(self.ipType)
                outStr += "\nLength:          "+ binascii.hexlify(self.length)
                outStr += "\nIdentification:  "+ binascii.hexlify(self.ipID)
                outStr += "\nFlags/offset:    "+ binascii.hexlify(self.flags)
                outStr += "\nTime to Live:    "+ binascii.hexlify(self.ttl)
                outStr += "\nProtocol:        "+ binascii.hexlify(self.ipProtocol)
                outStr += "\nChecksum:        "+ binascii.hexlify(self.checksum)
                outStr += "\nSource IP:       "+ socket.inet_ntoa(self.srcIP)
                outStr += "\nDest IP:         "+ socket.inet_ntoa(self.destIP)
                outStr += "\n************************************************"

                return outStr
        
        class setICMPHeader(object):
            def __init__(self, packetBytes):
                self.raw = packetBytes[34:42]
                self.data = packetBytes[42:]
                self.header = struct.unpack("1s1s2s4s", self.raw)
                self.icmpType = self.header[0]
                self.code = self.header[1]
                self.checksum = self.header[2]
                self.headerData = self.header[3]

            def getICMPHeader(self):
                return (self.icmpType, self.code, self.checksum, 
                        self.headerData)
                
            def __repr__(self):
                outStr = "******************_ICMP_HEADER_*****************"
                outStr += "\nType of Msg:     "+ binascii.hexlify(self.icmpType)
                outStr += "\nCode:            "+ binascii.hexlify(self.code)
                outStr += "\nChecksum:        "+ binascii.hexlify(self.checksum)
                outStr += "\nHeader data:     "+ binascii.hexlify(self.headerData)
                #outStr += "\nData:            "+ binascii.hexlify(self.data)
                outStr += "\n************************************************\n"

                return outStr


        def getMACaddress(self, destIP):
            
            destMAC = ''

            # loop over interfaces until find one that matches dest
            for net in self.netList:
                netIP = netifaces.ifaddresses(net)[2][0]['addr']
                netMAC = netifaces.ifaddresses(net)[17][0]['addr']

                print destIP, netIP, netMAC

                if destIP == netIP:
                    destMAC = netMAC

            return mactobinary(destMAC)

        def constructARPresponse(self):
           
            # create copies of headers
            new_ethHeader = deepcopy(self.ethHeader)
            new_arpHeader = deepcopy(self.arpHeader)

            # change arp op code
            new_arpHeader.opcode = '\x00\x02'

            # swap IPs
            new_arpHeader.srcIP = self.arpHeader.destIP
            new_arpHeader.destIP = self.arpHeader.srcIP 

            # source MAC becomes dest MAC
            new_ethHeader.destMAC = self.ethHeader.srcMAC
            new_arpHeader.destMAC = self.arpHeader.srcMAC

            # find MAC address for destIP
            new_MAC = self.getMACaddress(socket.inet_ntoa(self.arpHeader.destIP))
            
            # fill in hex version of dest MAC
            new_ethHeader.srcMAC = new_MAC
            new_arpHeader.srcMAC = new_MAC

            # return tuple objects for each header
            tup_newEthHeader = new_ethHeader.getEthHeader()
            tup_newARPHeader = new_arpHeader.getARPHeader()

            # pack header to binary
            bin_ethHeader = struct.pack("6s6s2s", *tup_newEthHeader)
            bin_arpHeader = struct.pack("2s2s1s1s2s6s4s6s4s", *tup_newARPHeader)

            # combine ethernet and arp headers
            new_packet = bin_ethHeader + bin_arpHeader
            
            return new_packet



        def constructICMPEchoReply(self):
           
            # create copies of headers
            new_ethHeader = deepcopy(self.ethHeader)
            new_ipHeader = deepcopy(self.ipHeader)
            new_icmpHeader = deepcopy(self.icmpHeader)
            
            # swap MACs
            new_ethHeader.srcMAC = self.ethHeader.destMAC
            new_ethHeader.destMAC = self.ethHeader.srcMAC
            
            # swap IPs
            new_ipHeader.srcIP = self.ipHeader.destIP
            new_ipHeader.destIP = self.ipHeader.srcIP

            # change type of msg
            new_icmpHeader.icmpType = '\x00'

            # return tuple objects for each header
            tup_newEthHeader = new_ethHeader.getEthHeader()
            tup_newIPHeader = new_ipHeader.getIPHeader()
            tup_newICMPHeader = new_icmpHeader.getICMPHeader()

            # pack back to binary
            bin_ethHeader = struct.pack("6s6s2s", *tup_newEthHeader)
            bin_ipHeader = struct.pack("1s1s2s2s2s1s1s2s4s4s", *tup_newIPHeader)
            bin_icmpHeader = struct.pack("1s1s2s4s", *tup_newICMPHeader)

            # combine eth, ip, and icmp headers and icmp data
            new_packet = bin_ethHeader + bin_ipHeader + bin_icmpHeader + new_icmpHeader.data
            
            return new_packet

        
        def verifyTTL(self):
            
            hexTTL = binascii.hexlify(self.ipHeader.ttl)
            intTTL = int(hexTTL, 16)
            intTTL -= 1

            if intTTL < 1:
                return False

            else:
                newHexTTL = hex(intTTL)
                self.ipHeader.ttl = binascii.unhexlify(newHexTTL[2:])
                return True
        # Heavily influenced by this: 
        #   https://www.codeproject.com/Tips/460867/Python-Implementation-of-IP-Checksum
        def checksum(header):
            csum = 0
            pos = 0
            result = 0

            while queue > 1:
                chunk = int((str('%02x' % (header[pos],)) + str('%02x' % (header[pos+1],))), 16)
                csum += chunk
                queue -= 2
                pos -= 2
            if queue:
                csum += header[pos]

            csum = (csum >> 16) + (csum & 0xffff)
            csum += (csum >> 16)
            result = (~csum) & 0xffff

            return result


    def getPackets(self):
        while True:
            raw_packet, addr = self.socket.recvfrom(self.maxPacketSize)
            fp = self.filePacket(raw_packet)
            fp.setPacketType()
            
            if fp.packetType == "ARP":
                fp.displayPacket("in")
                arp_packet = fp.constructARPresponse()
                fp.displayPacket("out")
                self.socket.sendto(arp_packet, addr)
                time.sleep(3)
            
            if fp.packetType == "ICMP":
                fp.displayPacket("in")
            
                # decrement TTL
                ttlFlag = fp.verifyTTL()
                
                # get checksum
                
                
                # get routing nextHop
                #print addr[0], addr[1:]
                
                # construct ICMP
                icmp_packet = fp.constructICMPEchoReply()
                fp.displayPacket("out")
                
                self.socket.sendto(icmp_packet, addr)
                #time.sleep(3)

#http://stackoverflow.com/questions/2986702/need-some-help-converting-a-mac-address-to-binary-data-for-use-in-an-ethernet-fr
def mactobinary(mac):
  return binascii.unhexlify(mac.replace(':', ''))

def parseForwardingTable():

    forwardingTable = {}
    
    routingTables = ['r1-table.txt', 'r2-table.txt']

    for rt in routingTables:
        with open(rt, 'r') as fp:
            for line in fp:
                lineParts = line.rstrip().split(' ')
                prefixParts = lineParts[0].split('/')
                prefix = prefixParts[0]
                prefixLen = int(prefixParts[1])

                nextHop = lineParts[1]
                interface = lineParts[2]
                
                router = rt[0:2]

                if router in forwardingTable:
                    forwardingTable[router].append([prefix, prefixLen, nextHop, interface])
                else:
                    forwardingTable[router] = [[prefix, prefixLen, nextHop, interface]]

    print forwardingTable

    return forwardingTable

def routingLookup(forwardingTable, srcIP, destIP):
    
    ipSub = {16: 4, 24: 6}

    # get which router from ip?
    # assume working with r1
    lookupTable = forwardingTable['r1']
    for entry in lookupTable:
        prefix = entry[0]
        prefixLen = entry[1]
        nextHop = entry[2]
        interface = entry[3]

        matchCheck = prefix[:ipSub[prefixLen]]

        destCheck = destIP[:ipSub[prefixLen]]

        if destCheck == matchCheck:
            if nextHop == '-':
                print destCheck, matchCheck, destIP, interface
            else:
                print destCheck, matchCheck, nextHop, interface




def main(argv):

    ft = parseForwardingTable()
    routingLookup(ft, '10.1.0.1', '10.3.0.1')
    routingLookup(ft, '10.1.0.1', '10.1.1.5')

    vr = virtualRouter()
    vr.getPackets()

if __name__ == "__main__":
    main(sys.argv)
