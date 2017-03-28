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
        #s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x003))
        print "Socket created correctly."
        print s
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit(-1)

    '''
    http://stackoverflow.com/questions/24415294/python-arp-sniffing-raw-socket-no-reply-packets
    '''
    while True:
        packet = s.recvfrom(2048)
        
        
        ethernet_header = packet[0][0:14]
        ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

        arp_header = packet[0][14:42]
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

        # skip non-ARP packets
        ethertype = ethernet_detailed[2]


        #if ethertype not in ['\x08\x06', '\x00\x08'] :
        if ethertype != '\x08\x06':
            #print "narp narp snarf"
            continue
       
        #elif ethertype == '\x00\x08':
        #    print i
        #    print 'ICMP echo request'
 

        elif ethertype == '\x08\x06':
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
            new_arp_detailed_list = list(arp_detailed)
            
            # swap IPs
            new_arp_detailed_list[6] = arp_detailed[8]
            new_arp_detailed_list[8] = arp_detailed[6]

            # source MAC becomes dest MAC
            new_arp_detailed_list[7] = arp_detailed[5]

            # fill in hex version of dest MAC
            new_arp_detailed_list[5] = mactobinary(dest_MAC)

            # cast back to tuple -- might not be needed?
            new_arp_detailed = tuple(new_arp_detailed_list)

            # pack back to binary
            '''
            http://stackoverflow.com/questions/16368263/python-struct-pack-for-individual-elements-in-a-list
            '''
            new_arp_header = struct.pack("2s2s1s1s2s6s4s6s4s", *new_arp_detailed)

            # combine ethernet and arp headers
            new_packet = ethernet_header + new_arp_header      

            # send new packet to addr received from old packet
            s.sendto(new_packet, packet[1])
            
            while 1:
                icmp_packet = s.recvfrom(1024)
 
                eth_header = icmp_packet[0][0:14]
                eth_detailed = struct.unpack("!6s6s2s", ethernet_header)

                ip_header = icmp_packet[0][14:34]
                #ip_header = icmp_packet[0][0:20]
                ip_detailed = struct.unpack("!1s1s2s2s2s1s1s2s4s4s", ip_header)

                icmp_header = icmp_packet[0][34:42]
                #icmp_header = icmp_packet[0][20:28]
                icmp_detailed = struct.unpack("!1s1s2s4s", icmp_header)

                #if icmp_detailed[0] == '\x08':
                if icmp_header[0] == '\x08':
                    print "icmp icmp icmp"
                    print "ICMP Type:", binascii.hexlify(icmp_header[0])
                  
                    print binascii.hexlify(icmp_packet[0][34])
                    print len(binascii.hexlify(icmp_packet[0]))
                    
                    new_icmp_packet = eth_header + ip_header + '\x00' + icmp_header[1:] + icmp_packet[0][42:]
                    #new_icmp_packet = ip_header + '\x00' + icmp_header[1:]              
    
                    print len(binascii.hexlify(new_icmp_packet))
                    
                    print binascii.hexlify(new_icmp_packet[34])
                    s.sendto(new_icmp_packet, icmp_packet[1])


if __name__ == "__main__":
    main(sys.argv)
