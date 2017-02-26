#!/usr/bin/python

'''
Developer: Adam Terwilliger
Version: February 22, 2017
Purpose: CIS 457 Project 2 Part 1
Details: UDP File Transfer

Server program
'''
import socket, os, sys, math, time

class filePacket(object):
	def __init__(self, size, index, data, last):
		self.size = size
		self.index = index
		self.data = data
		self.last = last 
		self.ackRecv = 0

	def __str__(self):
		return "Size:{}\nIndex:{}\nLast:{}\nENDOFHEADER{}".format(self.size, self.index, self.last, self.data)

	def __repr__(self):
		return str(self)

def main(argv):

	host = ''

	if len(argv) == 2:
		port = int(argv[1])

	else:
		port = raw_input('port: ')

		# check for non-characters and negative or large port numbers
		while not port.isdigit() or int(port) < 0 or int(port) > 65536:
			print "Invalid Port Number, try again."
			port = raw_input('port: ')

		# cast port only when know it's valid
		port = int(port)

	print "Waiting for client(s) to request file(s)..."	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, port))

	s.settimeout(3.0)

	filename, client_addr = s.recvfrom(1024)
	if filename in os.listdir("."):
		
		# receive filename from client
		print ("\nFile request received from client for: {}".format(filename))
	
	else:
		print "Not a valid file"
		sys.exit(-1)	

	windowSize = 5	
	packetDataSize = 32
	fileSize = os.path.getsize(filename)
	numberOfPackets = int(math.ceil(float(fileSize) / float(packetDataSize)))
	currentWindow = []
	highestPacketID = 0

	with open(filename, 'r') as myfile:
		
		# read first five packets
		for i in range(windowSize):
			fileChunk = myfile.read(packetDataSize)
			packet = filePacket(packetDataSize, i, fileChunk, 0)
			currentWindow.append(packet)			
			highestPacketID += 1

		for packet in currentWindow:
			print "Sending packet {}".format(packet.index)
			s.sendto(str(packet), client_addr)
		
		# current ack list
		ackList = []
		
		while 1:
			
			# wait for acks
			try:
				# receive acknowledgments
				ack, client_addr = s.recvfrom(1024)
				print "Received acknowledgment from client for packet {}".format(ack)
				ackList.append(int(ack))
				
			except:
				
				#check ack list
				ackSortedList = sorted(ackList)
				numConsAck = 0
				print "ackSortedList:", ackSortedList
				for i in range(len(ackSortedList)-1):
					if ackSortedList[i+1] - ackSortedList[i] == 1:
						numConsAck +=1

				print numConsAck+1
				print numberOfPackets
				print highestPacketID
	
				# take min of number of consecutive acknowledgments and num packets left
				for i in range(min(numConsAck+1, numberOfPackets - highestPacketID)):
					
					print "whyyyyyyy"
					# print current window			
					windowString = ''
					for packet in currentWindow:
						windowString += " " + str(packet.index) + " "
			
					print windowString
	
					currentWindow.pop(0)

					fileChunk = myfile.read(packetDataSize)
					
					packet = filePacket(packetDataSize, highestPacketID, fileChunk, 0)
					
					if packet.index == numberOfPackets:
						packet.last = 1
					
					currentWindow.append(packet)
					highestPacketID += 1
					print highestPacketID, numberOfPackets		
				
				for packet in currentWindow:
					print "Sending packet {}".format(packet.index)
					s.sendto(str(packet), client_addr)
				
				if highestPacketID == numberOfPackets:
					break

				# reset ack list	
				ackList = []

			

	s.close()

if __name__ == "__main__":
    main(sys.argv)

'''

		# read this file
		packetDataSize = 32
		packetIndex = 0
		packetList = []
		fileSize = os.path.getsize(filename)
		numberOfPackets = math.ceil(float(fileSize) / float(packetDataSize))
		windowSize = 5
		leftMostWindowPacket = 0
		

		with open(filename, 'r') as myfile:
			
			# read first five packets
			for i in range(windowSize):
				fileChunk = myfile.read(packetDataSize)
				x = filePacket(packetDataSize, packetIndex, fileChunk, 0)
				packetList.append(x)
				packetIndex+=1

			# send first five packets
			for packet in packetList:
				print "Sending packet {}".format(packet.index)
				s.sendto(str(packet), client_addr)

			# print current window			
			windowString = ''
			for packet in packetList:
					windowString += " " + str(packet.index) + " "
			print "Current Window:", windowString
		
			while 1:
				try:
					# get acknowledgments
					ack, client_addr = s.recvfrom(1024)
					print "Received acknowledgment from client for packet {}".format(ack)

					minPacket = 99999
					maxPacket = -1
					
					for i in range(len(packetList)):

						packIndex = packetList[i].index

						if packIndex < minPacket:
							minPacket = packIndex
						if packIndex > maxPacket:
							maxPacket = packIndex

						if int(ack) == packIndex:
							packetList[i].ackRecv = 1
							packetList.pop(i)

					# when do i slide window?
					#if (packetList[0].ackRecv == 1):
					if len(packetList) != windowSize and (maxPacket - minPacket) < (windowSize - 1):

					#print "min: {}, max: {}".format(minPacket, maxPacket)

					#if (maxPacket - minPacket) < (windowSize - 1):

						# read next line of file
						fileChunk = myfile.read(packetDataSize)
						x = filePacket(packetDataSize, packetIndex, fileChunk, 0)
						packetList.append(x)
						packetIndex+=1
	
						sleep(1)					

						# send new packet
						print "Sending packet {}".format(x.index)
						s.sendto(str(x), client_addr)
						
						if x.index == numberOfPackets:
							x.last = 1
						
							# send new packet
							print "Sending packet {}".format(x.index)
							s.sendto(str(x), client_addr)
							
							break
					
					#elif (packetList[0].ackRecv == 0 and packetIndex > 4):
						#resend because error
						#print "oh my"

				except:	
					print "Did not receive acknowledgment from client for packet {}".format(packetList[0].index)
						
					windowString = ''
					for packet in packetList:
						windowString += " " + str(packet.index) + " "
					print "Current Window:", windowString
						
					# resend packet
					print "Resending packet {}".format(packetList[0].index)
					s.sendto(str(packetList[0]), client_addr)
'''
