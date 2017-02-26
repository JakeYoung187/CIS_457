'''
server application to process requests for file transfers
'''

import socket
import os
import struct

class Server(object):
    
    def __init__(self, port=3490):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('',self.port))
        self.socket.settimeout(2)
        
    def serve(self):
        running = True
        while running:
            try:
                data, clientAddress = self.socket.recvfrom(self.port)
                print ('Received file request message')
                if int(self.getCheckSum(data)) == 0: #we got right data and its a file request
                    fileToFind = ''
                    dataAsList = data.split()
                    dataAsHex = [hex(int(elem, 16)) for elem in dataAsList]
                    for i in range(len(dataAsHex)-2):
                        fileToFind += str(unichr(int(dataAsHex[i],16)))
                    
                    if self.verifyFileExists(fileToFind):  
                        pkt = b'\x03' #byte 03 is the type of the packet
                        fileSize = os.path.getsize(fileToFind)
                        pkt += struct.pack('!L', fileSize)
                        hexString = self.getHexStringFromBytes(pkt)
                        checkSumAsInt = self.getCheckSum(hexString)
                        pkt += struct.pack('!B', checkSumAsInt)
                        self.socket.sendto(pkt, clientAddress)
                        nbrOfTimeouts = 0
                        while True:
                            try: 
                                ackMsg, clientAddress = self.socket.recvfrom(self.port)
                                if ackMsg:
                                    print('recv file size ack')
                                    break
                            except socket.timeout:
                                nbrOfTimeouts += 1
                                self.socket.sendto(pkt, clientAddress)
                                if nbrOfTimeouts > 9: #break out and continue
                                    break 
                        print('finding file {}'.format(fileToFind))
                        with open(fileToFind, "rb") as in_file:
                            hasMoreBytes = True
                            windowToSend = []
                            while hasMoreBytes:
                                piece = in_file.read(1021) #read in 1021 bytes of data at a time
                                if piece != "":
                                    piece += (b'\0') #response type
                                    seqIndex = len(windowToSend)
                                    piece += str(self.getSequenceNumberByte(seqIndex))
                                    hexString = self.getHexStringFromBytes(piece)
                                    checkSumAsInt = self.getCheckSum(hexString)
                                    checkSumByte = struct.pack('!B', checkSumAsInt)
                                    piece += checkSumByte
                                    windowToSend.append(piece)
                                if len(windowToSend) == 5 or piece == "":
                                    self.ensureWindowIsSent(windowToSend, clientAddress)
                                    windowToSend = []
                                if piece == "":
                                    hasMoreBytes = False
                                    break # end of file
                                      
                    else: #we have no file to send
                        print('File not found') #send this back to client
                else:
                    print('bad check sum ... need file to be resent')
            except socket.timeout:
                print('packet not received')
                        
            except KeyboardInterrupt:
                running = False
                break
            
    def getSequenceNumberByte(self, seqNumAsInt):
        bytes = {0: b'\x00', 1: b'\x01', 2: b'\x02', 3: b'\x03', 4: b'\x04'}
        return bytes[seqNumAsInt]
    
    def getWindowSizes(self, fileSize):
        '''
        return a list of window sizes
        '''
        windows = []
        nbrOfFullWindows = fileSize/5120 #1024*5
        for window in range(nbrOfFullWindows):
            windows.append(5)
        leftOverData = fileSize%5120
        windowSize = int(math.ceil(leftOverData/1024.0)) #add one for empty string packet
        windows.append(windowSize)
        return windows
            
    def getHexStringFromBytes(self, bytes):
        hexVals = [elem.encode("hex") for elem in bytes]
        hexString = ''
        for i in range(len(hexVals)):
            hex = str(hexVals[i])
            hexString += (hex + ' ')
        return hexString.strip()
    
    def getCheckSum(self, hexString):
        '''
        Method calculates check sum to send back to client
        '''
        hexSections = hexString.split()
        result = 0
        for piece in hexSections:
            intPiece = int(piece, 16)
            result += intPiece
            binResult = bin(result)
            if len(binResult) == 11:
                result -= 256
                result += 1
        binResult = bin(result)[2:]
        while(len(binResult) < 8):
            binResult = ('0' + binResult)
        onesComp = ''
        for bit in binResult:
            if bit == '0':
                onesComp += '1'
            if bit == '1':
                onesComp += '0'
        finalByte = int(onesComp, 2)
        return finalByte
    
    def verifyFileExists(self, filePath):
        '''
        Method verifies that the filepath requested by the client is available
        '''
        if os.path.isfile(filePath):
            return True
        return False
    
    def ensureWindowIsSent(self, currPackets, clientAddress):
        '''
        Given a window of 5 packets... this method makes sure those packets get to the client correctly
        '''
        for pkt in currPackets: #first send the x packets right away
            self.socket.sendto(pkt, clientAddress)
            print ('Sending packet of data')
        ackWindowSize = 5
        if len(currPackets) < 5:
            ackWindowSize = len(currPackets)
        acksReceived = ['' for pkt in range(ackWindowSize)]
        while True: #try to recv as many acks as possible
            try:
                data, clientAddress = self.socket.recvfrom(self.port) #get ack back
                if data == "":
                    print ('Received empty string ack indicating file is done')
                    return True #client received all data
                dataList = [elem.encode("hex") for elem in data]
                print('Received Ack {}'.format(dataList))
                hexString = self.getHexStringFromBytes(data)
                checkSum = self.getCheckSum(hexString)
                responseType = int(dataList[0],16)
                if responseType == 1 and checkSum == 0:
                    seqNum = int(dataList[1],16)
                    acksReceived[seqNum] = data
                    if self.areAllAcksReceived(acksReceived):
                        break
            except socket.timeout:
                #send packets that are need to be resent (ack lost or corrupted)
                print(acksReceived)
                for ackIndex in range(len(acksReceived)):
                    if ackIndex < len(currPackets):
                        if acksReceived[ackIndex] == '': #ack not receieved... re-send
                            print('Resending lost / corrupted data')
                            self.socket.sendto(currPackets[ackIndex], clientAddress)
                
        return True #window was sent
                
    def areAllAcksReceived(self, acksReceived):
        if '' in acksReceived:
            return False
#         if len(acksReceived) > 0:
#             if acksReceived[len(acksReceived)-1] == '': #last window will have empty string packet
#                 return True
        return True        
            
            
if __name__ == "__main__":
    portNbr = raw_input("Please enter port to listen on: ")
    Server(int(portNbr)).serve()
