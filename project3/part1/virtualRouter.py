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
import struct
import binascii

'''
http://stackoverflow.com/questions/2986702/need-some-help-converting-a-mac-address-to-binary-data-for-use-in-an-ethernet-fr
'''
def mactobinary(mac):
  return binascii.unhexlify(mac.replace(':', ''))


def main(argv):    

    try: 
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x003))
        print "Socket created correctly."
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit(-1)

    '''
    http://stackoverflow.com/questions/24415294/python-arp-sniffing-raw-socket-no-reply-packets
    '''
    while True:
        packet = s.recvfrom(2048)
        
        
        eth_header = packet[0][0:14]
        eth_detailed = struct.unpack("!6s6s2s", eth_header)

        arp_header = packet[0][14:42]
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

        # skip non-ARP packets
        eth_type = eth_detailed[2]

        #if ethertype not in ['\x08\x06', '\x00\x08'] :
        if eth_type != '\x08\x06':
            #print "narp narp snarf"
            continue
       
        #elif ethertype == '\x00\x08':
        #    print i
        #    print 'ICMP echo request'
 

        elif eth_type == '\x08\x06':
            print "****************_INCOMING_PACKET_***************"
            print "****************_ARP_REQUEST_*******************"
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
            print "*************************************************\n"    

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

            # pack back to binary
            '''
            http://stackoverflow.com/questions/16368263/python-struct-pack-for-individual-elements-in-a-list
            '''
            new_eth_header = struct.pack("6s6s2s", *new_eth_detailed)
            new_arp_header = struct.pack("2s2s1s1s2s6s4s6s4s", *new_arp_detailed)

            # combine ethernet and arp headers
            new_packet = new_eth_header + new_arp_header      

            ethernet_header = new_packet[0:14]
            ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

            arp_header = new_packet[14:42]
            arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

            ethertype = ethernet_detailed[2]

            print "****************_OUTGOING_PACKET_***************"
            print "****************_ARP_REPLY_*********************"
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
            print "*************************************************\n"    

            # send new packet to addr received from old packet
            s.sendto(new_packet, packet[1])
            
            while 1:
                icmp_packet = s.recvfrom(1024)
 
                #eth_header = icmp_packet[0][0:14]
                #eth_detailed = struct.unpack("!6s6s2s", ethernet_header)

                #ip_header = icmp_packet[0][14:34]
                ip_header = icmp_packet[0][0:20]
                ip_detailed = struct.unpack("!1s1s2s2s2s1s1s2s4s4s", ip_header)
                #ip_ver, ip_type, ip_len, ip_id, ip_flags, ip_ttl, ip_proto, \
                #    ip_checksum, ip_srcIP, ip_destIP = struct.unpack("!BBHHHBBHII", ip_header)


                #icmp_header = icmp_packet[0][34:42]
                icmp_header = icmp_packet[0][20:28]
                icmp_detailed = struct.unpack("!1s1s2s4s", icmp_header)
		#icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq = struct.unpack("bbHHh", icmp_header)

                #if icmp_detailed[0] == '\x08':
                #if icmp_type == 8:
                ip_type = ip_detailed[1]
                ip_protocol = ip_detailed[6]

                if ip_type == '\x00' and ip_protocol == '\x01':
                #if True:
                    print "****************_INCOMING_PACKET_***************"
                    print "****************_ICMP_ECHO_REQUEST_*************"
                    print "****************_IP_HEADER_*********************"
                    print "Version/IHL:     ", binascii.hexlify(ip_detailed[0])
                    print "Type of service: ", binascii.hexlify(ip_detailed[1])
                    print "Length:          ", binascii.hexlify(ip_detailed[2])
                    print "Identification:  ", binascii.hexlify(ip_detailed[3])
                    print "Flags/offset:    ", binascii.hexlify(ip_detailed[4])
                    print "Time to Live:    ", binascii.hexlify(ip_detailed[5])
                    print "Protocol:        ", binascii.hexlify(ip_detailed[6])
                    print "Source IP:       ", binascii.hexlify(ip_detailed[7])
                    print "Dest IP:         ", binascii.hexlify(ip_detailed[8])
                    #print "Source IP:      ", socket.inet_ntoa(ip_detailed[7])
                    #print "Dest IP:        ", socket.inet_ntoa(ip_detailed[8])
                    print "************************************************"
                    print "******************_ICMP_HEADER_******************"
                    print "Type of Msg:     ", binascii.hexlify(arp_detailed[0])
                    print "Code:            ", binascii.hexlify(arp_detailed[1])
                    print "Checksum:        ", binascii.hexlify(arp_detailed[2])
                    print "Header data:     ", binascii.hexlify(arp_detailed[3])
                    
                    '''
                    print "ip_ver: {}".format(ip_ver)
                    print "ip_type: {}".format(ip_type)
                    print "ip_len: {}".format(ip_len)
                    print "ip_id: {}".format(ip_id)
                    print "ip_flags: {}".format(ip_flags)
                    print "ip_ttl: {}".format(ip_ttl)
                    print "ip_proto: {}".format(ip_proto)
                    print "ip_checksum: {}".format(ip_checksum)
                    print "ip_srcIP: {}".format(ip_srcIP)
                    print "ip_destIP: {}".format(ip_destIP)
                
                    print "icmp_type: {}".format(icmp_type)
		    print "icmp_code: {}".format(icmp_code)
		    print "icmp_checksum: {}".format(icmp_checksum)
		    print "p_id: {}".format(icmp_id)
		    print "icmp_seq: {}".format(icmp_seq)
                    '''
                    #s.sendto(new_icmp_packet, icmp_packet[1])

if __name__ == "__main__":
    main(sys.argv)
