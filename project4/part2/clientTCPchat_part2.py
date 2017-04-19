#!/usr/bin/python

'''
Developers:  Adam Terwilliger, Ellysa Stanton
Version:	 April 17, 2017
Objective:	 CIS 457 Project 4 Part 2
Details: 	 TCP Encrypted Chat Program
Credits:	 Josh Engelsma, Andrew Kalafut
'''

import sys, socket, select, re

'''
Client for encrypted TCP chat that can execute
	numerous commands like sending messages,
	listing active users, and kicking users
'''
class clientTCPchat(object):

	def __init__(self, host='127.0.0.1', port=1234, name=None):
		self.host = host
		self.port = port
		self.name = name
		self.maxBufSize = 1024
		self.active = True
		self.prompt='[{}]> '.format(name)
		
		self.pubKey = None
		self.symKey = None

		try:
			# set up TCP socket and connect to host/port
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((host, self.port))
			print('Welcome to The Office fanatics chatroom.')

			# send username to server in setup
			self.sock.send('NAME: ' + self.name) 
			data = self.sock.recv(self.maxBufSize)
			
			# get client address and set it
			addr = data.split('CLIENT: ')[1]
			self.prompt = '[{}]> '.format(name)

		# catch all errors in setup
		except socket.error, e:
			print 'Uh oh...something went wrong connecting to chat server'
			sys.exit(1)

	def loadRSApubKey(self):
		from cryptography.hazmat.backends import default_backend
		from cryptography.hazmat.primitives.serialization import load_pem_public_key
		pub_data = open('RSApub.pem','r').read()
		self.pubKey = load_pem_public_key(pub_data, backend=default_backend())
		print "Loaded public key..."

	def generateSymmetricKey(self):
		from cryptography.fernet import Fernet
		self.symKey = Fernet.generate_key()
		print "Generated symmetric key..."

	def encryptSymKey(self):
		from cryptography.hazmat.primitives.asymmetric import padding
		from cryptography.hazmat.primitives import hashes
		ciphertext = self.pubKey.encrypt(self.symKey,
			padding.OAEP(
            	mgf=padding.MGF1(algorithm=hashes.SHA1()),
            	algorithm=hashes.SHA1(),
            	label=None
        	)
    	)
		print "Encrypted symmetric key with public key..."
		return ciphertext

	def setupEncryption(self):
		self.loadRSApubKey()
		self.generateSymmetricKey()
		ctSymKey = self.encryptSymKey()
	
		print "Sent symmetric key ciphertext to server..."
		self.sock.send('ctSymKey: ' + ctSymKey)

		# receive confirmation for sym key
		cfMsg = self.sock.recv(self.maxBufSize)
		print cfMsg

	def encryptTraffic(self, msg):
		from cryptography.fernet import Fernet
		f = Fernet(self.symKey)	
		token = f.encrypt(msg)
		return token

	def decryptTraffic(self, token):
		from cryptography.fernet import Fernet
		f = Fernet(self.symKey)
		print "Received encrypted msg from server:\n{}".format(token)
		msg = f.decrypt(token)
		print "Decrypted msg using symmetric key:"
		return msg

	def execute(self):

		while self.active:
			try:
				# add username prompt and flush output
				sys.stdout.write(self.prompt)
				sys.stdout.flush()

				# wait for input from stdin & socket
				inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])

				# read next line or break
				for i in inputready:
					if i == 0:
						data = sys.stdin.readline().strip()
						if data: 
							# send encrypted data to server
							eData = self.encryptTraffic(data)
							self.sock.send(eData)
					elif i == self.sock:
						# receive encrypted data from server
						eData = self.sock.recv(self.maxBufSize)
						data = self.decryptTraffic(eData)
						if data == 'You are the weakest link...goodbye.':
							print 'Admin booted you from chat.'
							print data
							self.active = False
							break
						if not data:
							print 'Shutting down.'
							self.active = False
							break
						else:
							sys.stdout.write(data + '\n')
							sys.stdout.flush()
							
			except KeyboardInterrupt:
				print '...received interrupt.\nCome again soon!'
				#self.sock.close()
				break

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
	
def getHostAndPort(argsFromCommandLine):

	# either enter host/port by command line or user input
	if len(argsFromCommandLine) == 4:
		host = argsFromCommandLine[1]
		port = int(argsFromCommandLine[2])
		username = argsFromCommandLine[3]

	else:
		
		username = raw_input("username: ")
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

	return host, port, username

def main(argv):

	host, port, username = getHostAndPort(argv)
	c = clientTCPchat(host, port, username)
	c.setupEncryption()
	c.execute()

if __name__ == "__main__":
	main(sys.argv)

