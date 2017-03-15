'''
Client application for requesting a file
'''

import socket
import struct
import math

class Client(object):
    
    def __init__(self, port=3490, ipToSend=''):
        self.port = port
        self.ipToSend = ipToSend
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket.bind(('',self.port))
        self.fileSize = 0
        self.socket.settimeout(4)   
        
    def requestFiles(self):
        running = True
        while running:
            try:
                fileRequested = raw_input("Please enter file to request: ")
                fileNameAsHex = [elem.encode("hex") for elem in fileRequested]
                hexString = self.getHexFromHex(fileNameAsHex)
                hexString += (' ' + '00') #if file request send zeros
                checkSum = str(self.getCheckSum(hexString))
                checkSum = checkSum[2:]
                fileNameAsHex.append('00')#request type first
                fileNameAsHex.append(checkSum)#checksum last
                fileRequestAsStr = ''
                for i in range(len(fileNameAsHex)):
                    fileRequestAsStr += (fileNameAsHex[i] + ' ')
                fileRequestAsStr = fileRequestAsStr.strip()
                print('Requesting file {}'.format(fileRequestAsStr))
                self.socket.sendto(fileRequestAsStr, (self.ipToSend, self.port)) #send request for file
                self.fileSize = self.getFileSize()
                windows = self.getWindowSizes(self.fileSize)
                recvBuffer = []
                self.recvPackets(fileRequested, windows, recvBuffer, (self.ipToSend, self.port))
                       
            except KeyboardInterrupt:
                running = False
                break
            
    def sendAckForPacket(self, candidate, serverAddress):
        candidateAsList = [elem.encode("hex") for elem in candidate]
        candidateSeqNumAsInt = int(candidateAsList[len(candidate)-2],16)
        responseType = 1
        currCheck = 0
        candidateAckMsg = struct.pack('!BBB', responseType, candidateSeqNumAsInt, currCheck)
        hexString = self.getHexStringFromBytes(candidateAckMsg)
        candidateCheckSum = int(self.getCheckSum(hexString),16)
        candidateAckMsg = struct.pack('!BBB', responseType, candidateSeqNumAsInt, candidateCheckSum)
        print('Sending Ack message to server')
        self.socket.sendto(candidateAckMsg, serverAddress)
                
    def orderPacketsCorrectly(self, windowSize, recvBuffer):
        '''
        Returns our window in the correct order
        '''
        originalOrder = recvBuffer
        newOrder = ['' for elem in range(windowSize)]
        for pkt in originalOrder:
            pktAsHexList = [elem.encode("hex") for elem in pkt]
            seqNum = pktAsHexList[len(pktAsHexList)-2]
            newOrder[int(seqNum, 16)] = pkt
        return newOrder
                
    def recvPackets(self, fileRequested, windows, recvBuffer, serverAddress):
        '''
        Method ensures that window of 5 is all recieved...
        '''
        firstPktForNextWindow = None
        bytesRecv = 0
        with open(fileRequested, "wb") as out_file:
            for window in windows:
                recvBuffer = ['' for i in range(window)] #init recv Buffer to current window size
                if firstPktForNextWindow != None:
                    hexList = [elem.encode("hex") for elem in firstPktForNextWindow]
                    seqNum = int(hexList[len(hexList)-2],16)
                    recvBuffer[seqNum] = firstPktForNextWindow
                    bytesRecv += len(firstPktForNextWindow)
                    firstPktForNextWindow = None
                while True: #receive all packets server has for this window
                    try:
                        data, serverAddress = self.socket.recvfrom(self.port)
                
                        print('Receiving data packet')
                    
                        hexString = self.getHexStringFromBytes(data)
                        pktCheckSum = int(self.getCheckSum(hexString), 16)
                        hexVals = [elem.encode("hex") for elem in data]
                        type = 100
                        if len(hexVals) >= 3:
                            type = int(hexVals[len(hexVals)-3], 16)
                    
                        if pktCheckSum == 0 and type == 0: #check sum is correct and type is data pkt
                            seqNum = int(hexVals[len(hexVals)-2],16)
                            if recvBuffer[seqNum] == '': #first time recv good data packet for this window
                                self.sendAckForPacket(data, serverAddress)
                                recvBuffer[seqNum] = data
                                bytesRecv += len(data)
                                if bytesRecv >= self.fileSize:
                                    self.writeBytes(out_file, recvBuffer, window)
                            else: #data we received with seq number place is taken in recv buffer
                                if self.isDupePacket(data, recvBuffer): #ack was lost or corrupted
                                    self.sendAckForPacket(data, serverAddress) #resend ack
                                else: #next window is being sent
                                    #write whats in buffer now
                                    self.writeBytes(out_file, recvBuffer, window)
                                    recvBuffer = [] #empty buffer after writing
                                    firstPktForNextWindow = data
                                    self.sendAckForPacket(data, serverAddress)
                                    break
                    except:
                        print('server has nothing left to send')
                        break    
                            
    def writeBytes(self, out_file, recvBuffer, windowSize):
        orderedPkts = self.orderPacketsCorrectly(windowSize, recvBuffer)
        for pkt in orderedPkts:
            lenOfPktData = len(pkt) - 3
            out_file.write(pkt[:lenOfPktData]) #dont write checksum bytes and so on...
            out_file.flush()
    
    def getFileSize(self):
        fileSize = 0
        while True: #keep trying to get file size
            data, serverAddress = self.socket.recvfrom(self.port)
            hexString = self.getHexStringFromBytes(data)
            checkSum = int(self.getCheckSum(hexString), 16)
            if checkSum == 0: #we got the write file size
                data = data[1:-1] #remove checksum and type byte
                dataAsList = [elem.encode("hex") for elem in data]
                hexValue = ''.join(elem for elem in dataAsList)
                fileSize = int(hexValue, 16)
                self.socket.sendto('ACK', serverAddress)
                print('sending file size ack')
                return fileSize
            
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
    
    def getHexFromHex(self, bytes):
        hexString = ''
        for i in range(len(bytes)):
            hex = str(bytes[i])
            hexString += (hex + ' ')
        return hexString.strip()
    
    def getCheckSum(self, hexString):
        '''
        Method returns a check sum for a packet
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
        hexValue = hex(finalByte)
        
        return hexValue
    
    def isDupePacket(self, pkt, recvBuffer):
        pktAsList = [elem.encode("hex") for elem in pkt]
        for recPkt in recvBuffer:
            hexList = [elem.encode("hex") for elem in recPkt]
            if pktAsList == hexList:
                return True #dupe packet
        return False
        
if __name__ == "__main__":
    serverIP = raw_input("Please enter server ip address: ")
    serverPort = raw_input("Please enter port server is on: ")
    Client(int(serverPort), serverIP).requestFiles()
