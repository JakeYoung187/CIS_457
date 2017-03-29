#!/usr/bin/python

'''
Developer: Adam Terwilliger, Ellysa Stanton
Version: April 5, 2017
Purpose: CIS 457 Project 3 - Virtual Router
Details: Implementing a simplified version of a router in software
         in order to learn about the function of a router.
'''

import socket, os, sys, netifaces, struct, binascii, time

class virtualRouter(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_PACKET,socket.SOCK_RAW, 
                        socket.htons(0x003))

   class filePacket(object):
        def __init__(self, packetBytes, ethHeader=None, arpHeader=None,
                        ipHeader=None, icmpHeader=None):
            self.packetBytes = packetBytes
            self.ethHeader = ethHeader
            self.arpHeader = arpHeader
            self.ipHeader = ipHeader
            self.icmpHeader = icmpHeader
            self.maxPacketSize = 1024
            self.packetType = 'Unknown'

        def setPacketType(self):

            eth_raw = self.packetBytes[0:14]
            self.ethHeader = struct.unpack("!6s6s2s", eth_raw)

            # skip non-ARP packets
            eth_type = eth_detailed[2]

            if eth_type == '\x08\x06':
                self.packetType = 'ARP'

            else:
                ip_raw = self.packetBytes[14:34]
                self.ipHeader = struct.unpack("1s1s2s2s2s1s1s2s4s4s", ip_raw)

                ip_type = self.ipHeader[1]
                ip_protocol = self.ipHeader[6]
                
                if ip_type == '\x00' and ip_protocol == '\x01':
                    self.packetType = 'ICMP'

    '''
    def getPackets(self):
        while True:
            raw_packet, addr = self.socket.recvFrom(self.maxPacketSize)
            fp = filePacket(raw_packet)
            fp.setPacketType()

    '''



#http://stackoverflow.com/questions/2986702/need-some-help-converting-a-mac-address-to-binary-data-for-use-in-an-ethernet-fr

'''
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
        
        matchCheck = prefix[:ipSub[prefixLen]]

        destCheck = destIP[:ipSub[prefixLen]]

        if destCheck == matchCheck:
            if nextHop == '-':
                print destCheck, matchCheck, destIP
            else:
                print destCheck, matchCheck, nextHop

def main(argv):    

    ft = parseForwardingTable()

    routingLookup(ft, '10.1.0.1', '10.3.0.1')
    
    routingLookup(ft, '10.1.0.1', '10.1.1.5')
    
    try: 
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x003))
        print "Socket created correctly."
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit(-1)

    #http://stackoverflow.com/questions/24415294/python-arp-sniffing-raw-socket-no-reply-packets
    
    while True:

        packet = s.recvfrom(1024)
        
        eth_header = packet[0][0:14]
        eth_detailed = struct.unpack("!6s6s2s", eth_header)

        arp_header = packet[0][14:42]
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

        # skip non-ARP packets
        eth_type = eth_detailed[2]

        if eth_type == '\x08\x06':
            print "************************************************"    
            print "****************_INCOMING_PACKET_***************"
            print "****************_ARP_REQUEST_*******************"
            print "************************************************"    
            print "****************_ETHERNET_FRAME_****************"
            print "Dest MAC:        ", binascii.hexlify(eth_detailed[0])
            print "Source MAC:      ", binascii.hexlify(eth_detailed[1])
            print "Type:            ", binascii.hexlify(eth_detailed[2])
            print "************************************************"
            print "******************_ARP_HEADER_******************"
            print "Hardware type:   ", binascii.hexlify(arp_detailed[0])
            print "Protocol type:   ", binascii.hexlify(arp_detailed[1])
            print "Hardware size:   ", binascii.hexlify(arp_detailed[2])
            print "Protocol size:   ", binascii.hexlify(arp_detailed[3])
            print "Opcode:          ", binascii.hexlify(arp_detailed[4])
            print "Source MAC:      ", binascii.hexlify(arp_detailed[5])
            print "Source IP:       ", socket.inet_ntoa(arp_detailed[6])
            print "Dest MAC:        ", binascii.hexlify(arp_detailed[7])
            print "Dest IP:         ", socket.inet_ntoa(arp_detailed[8])
            print "************************************************\n"    

            # strings for ip addresses
            source_IP = socket.inet_ntoa(arp_detailed[6])
            dest_IP = socket.inet_ntoa(arp_detailed[8])

            # get list of network interfaces 
            net_list = netifaces.interfaces()
            
            # loop over interfaces until find one that matches dest
            for net in net_list:
                net_IP = netifaces.ifaddresses(net)[2][0]['addr']
                net_MAC = netifaces.ifaddresses(net)[17][0]['addr']

                if dest_IP == net_IP:
                    dest_MAC = net_MAC
            
            # tuples are immutable in python, copy to list
            new_eth_detailed_list = list(eth_detailed)
            new_arp_detailed_list = list(arp_detailed)

            # change arp op code
            new_arp_detailed_list[4] = '\x00\x02'

            # swap IPs
            new_arp_detailed_list[6] = arp_detailed[8]
            new_arp_detailed_list[8] = arp_detailed[6]

            # source MAC becomes dest MAC
            new_eth_detailed_list[0] = eth_detailed[1]
            new_arp_detailed_list[7] = arp_detailed[5]

            # fill in hex version of dest MAC
            new_eth_detailed_list[1] = mactobinary(dest_MAC)
            new_arp_detailed_list[5] = mactobinary(dest_MAC)

            # cast back to tuple -- might not be needed?
            new_eth_detailed = tuple(new_eth_detailed_list)
            new_arp_detailed = tuple(new_arp_detailed_list)
            
            #http://stackoverflow.com/questions/16368263/python-struct-pack-for-individual-elements-in-a-list
            
            # pack back to binary
            new_eth_header = struct.pack("6s6s2s", *new_eth_detailed)
            new_arp_header = struct.pack("2s2s1s1s2s6s4s6s4s", *new_arp_detailed)

            # combine ethernet and arp headers
            new_packet = new_eth_header + new_arp_header      

            ethernet_header = new_packet[0:14]
            ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

            arp_header = new_packet[14:42]
            arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

            ethertype = ethernet_detailed[2]

            print "************************************************"    
            print "****************_OUTGOING_PACKET_***************"
            print "****************_ARP_REPLY_*********************"
            print "************************************************"    
            print "****************_ETHERNET_FRAME_****************"
            print "Dest MAC:        ", binascii.hexlify(ethernet_detailed[0])
            print "Source MAC:      ", binascii.hexlify(ethernet_detailed[1])
            print "Type:            ", binascii.hexlify(ethertype)
            print "************************************************"
            print "******************_ARP_HEADER_******************"
            print "Hardware type:   ", binascii.hexlify(arp_detailed[0])
            print "Protocol type:   ", binascii.hexlify(arp_detailed[1])
            print "Hardware size:   ", binascii.hexlify(arp_detailed[2])
            print "Protocol size:   ", binascii.hexlify(arp_detailed[3])
            print "Opcode:          ", binascii.hexlify(arp_detailed[4])
            print "Source MAC:      ", binascii.hexlify(arp_detailed[5])
            print "Source IP:       ", socket.inet_ntoa(arp_detailed[6])
            print "Dest MAC:        ", binascii.hexlify(arp_detailed[7])
            print "Dest IP:         ", socket.inet_ntoa(arp_detailed[8])
            print "************************************************\n"    

            #print len(packet[0]), len(new_packet)

            # send new packet to addr received from old packet
            s.sendto(new_packet, packet[1])
           
            #time.sleep(1)
        
        elif eth_type != '\x08\x06':
            
            #icmp_packet = s.recvfrom(2048)

            icmp_packet = packet

            eth_header = icmp_packet[0][0:14]
            eth_detailed = struct.unpack("!6s6s2s", eth_header)

            ip_header = icmp_packet[0][14:34]
            ip_detailed = struct.unpack("1s1s2s2s2s1s1s2s4s4s", ip_header)
            #ip_ver, ip_type, ip_len, ip_id, ip_flags, ip_ttl, ip_proto, \
            #    ip_checksum, ip_srcIP, ip_destIP = struct.unpack("!BBHHHBBHII", ip_header)

            icmp_header = icmp_packet[0][34:42]
            icmp_detailed = struct.unpack("1s1s2s4s", icmp_header)
            #icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack("bbHHh", icmp_header)

            ip_type = ip_detailed[1]
            ip_protocol = ip_detailed[6]
            
            if ip_type == '\x00' and ip_protocol == '\x01':
                print "************************************************"    
                print "****************_INCOMING_PACKET_***************"
                print "****************_ICMP_ECHO_REQUEST_*************"
                print "************************************************"    
                print "****************_ETHERNET_FRAME_****************"
                print "Dest MAC:        ", binascii.hexlify(eth_detailed[0])
                print "Source MAC:      ", binascii.hexlify(eth_detailed[1])
                print "Type:            ", binascii.hexlify(eth_detailed[2])
                print "************************************************"
                print "****************_IP_HEADER_*********************"
                print "Version/IHL:     ", binascii.hexlify(ip_detailed[0])
                print "Type of service: ", binascii.hexlify(ip_detailed[1])
                print "Length:          ", binascii.hexlify(ip_detailed[2])
                print "Identification:  ", binascii.hexlify(ip_detailed[3])
                print "Flags/offset:    ", binascii.hexlify(ip_detailed[4])
                print "Time to Live:    ", binascii.hexlify(ip_detailed[5])
                print "Protocol:        ", binascii.hexlify(ip_detailed[6])
                print "Checksum:        ", binascii.hexlify(ip_detailed[7])
                print "Source IP:       ", socket.inet_ntoa(ip_detailed[8])
                print "Dest IP:         ", socket.inet_ntoa(ip_detailed[9])
                print "************************************************"
                print "******************_ICMP_HEADER_*****************"
                print "Type of Msg:     ", binascii.hexlify(icmp_detailed[0])
                print "Code:            ", binascii.hexlify(icmp_detailed[1])
                print "Checksum:        ", binascii.hexlify(icmp_detailed[2])
                print "Header data:     ", binascii.hexlify(icmp_detailed[3])
                print "************************************************\n"    
                
                # tuples are immutable in python, copy to list
                new_eth_detailed_list = list(eth_detailed)
                new_ip_detailed_list = list(ip_detailed)
                new_icmp_detailed_list = list(icmp_detailed)
               
                # swap IPs
                new_ip_detailed_list[8] = ip_detailed[9]
                new_ip_detailed_list[9] = ip_detailed[8]

                # swap MACs
                new_eth_detailed_list[0] = eth_detailed[1]
                new_eth_detailed_list[1] = eth_detailed[0]

                # change type of msg
                new_icmp_detailed_list[0] = '\x00'

                # cast back to tuple -- might not be needed?
                new_eth_detailed = tuple(new_eth_detailed_list)
                new_ip_detailed = tuple(new_ip_detailed_list)
                new_icmp_detailed = tuple(new_icmp_detailed_list)
                
                # pack back to binary
                new_eth_header = struct.pack("6s6s2s", *new_eth_detailed)
                new_ip_header = struct.pack("1s1s2s2s2s1s1s2s4s4s", *new_ip_detailed)
                new_icmp_header = struct.pack("1s1s2s4s", *new_icmp_detailed)

                # combine eth, ip, and icmp headers and icmp data
                new_icmp_packet = new_eth_header + new_ip_header + new_icmp_header + icmp_packet[0][42:]
                
                eth_header = new_icmp_packet[0:14]
                eth_detailed = struct.unpack("!6s6s2s", eth_header)

                ip_header = new_icmp_packet[14:34]
                ip_detailed = struct.unpack("1s1s2s2s2s1s1s2s4s4s", ip_header)

                icmp_header = new_icmp_packet[34:42]
                icmp_detailed = struct.unpack("1s1s2s4s", icmp_header)

                print "************************************************"    
                print "****************_OUTGOING_PACKET_***************"
                print "****************_ICMP_ECHO_REPLY_***************"
                print "************************************************"
                print "****************_ETHERNET_FRAME_****************"
                print "Dest MAC:        ", binascii.hexlify(eth_detailed[0])
                print "Source MAC:      ", binascii.hexlify(eth_detailed[1])
                print "Type:            ", binascii.hexlify(eth_detailed[2])
                print "************************************************"
                print "****************_IP_HEADER_*********************"
                print "Version/IHL:     ", binascii.hexlify(ip_detailed[0])
                print "Type of service: ", binascii.hexlify(ip_detailed[1])
                print "Length:          ", binascii.hexlify(ip_detailed[2])
                print "Identification:  ", binascii.hexlify(ip_detailed[3])
                print "Flags/offset:    ", binascii.hexlify(ip_detailed[4])
                print "Time to Live:    ", binascii.hexlify(ip_detailed[5])
                print "Protocol:        ", binascii.hexlify(ip_detailed[6])
                print "Checksum:        ", binascii.hexlify(ip_detailed[7])
                print "Source IP:       ", socket.inet_ntoa(ip_detailed[8])
                print "Dest IP:         ", socket.inet_ntoa(ip_detailed[9])
                print "************************************************"
                print "******************_ICMP_HEADER_*****************"
                print "Type of Msg:     ", binascii.hexlify(icmp_detailed[0])
                print "Code:            ", binascii.hexlify(icmp_detailed[1])
                print "Checksum:        ", binascii.hexlify(icmp_detailed[2])
                print "Header data:     ", binascii.hexlify(icmp_detailed[3])
                print "************************************************\n"

                #print len(icmp_packet[0]), len(new_icmp_packet)

                s.sendto(new_icmp_packet, icmp_packet[1])
'''
if __name__ == "__main__":
    main(sys.argv)
