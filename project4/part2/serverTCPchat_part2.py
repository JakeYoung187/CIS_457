#!/usr/bin/python

'''
Developers:  Adam Terwilliger, Ellysa Stanton
Version:     April 17, 2017
Objective:   CIS 457 Project 4 Part 2
Details:     TCP Encrypted Chat Program
Credits:     Josh Engelsma, Andrew Kalafut
'''

import sys, socket, select, signal

class serverTCPchat(object):
	def __init__(self, port=1234, backlog=5):
		self.port = port
		self.maxBufSize = 1024
		self.clients = 0
		self.clientmap = {}
		self.groupmap = {}
		self.outputs = []
		self.inputs = []
		self.privKey = None
		self.symKeyMap = {}
		self.adminPassword = 'boboddy'
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind(('',port))
		print ('Listening to port'.format(port))
		self.server.listen(backlog)
		signal.signal(signal.SIGINT, self.sighandler)
		
	def sighandler(self, signum, frame):
		print ('Shutting down server...')
		for o in self.outputs:
			o.close() 
		self.server.close()
	
	def loadRSAprivKey(self):
		from cryptography.hazmat.backends import default_backend
		from cryptography.hazmat.primitives.serialization import load_pem_private_key
		priv_data = open('RSApriv.pem','r').read()
		self.privKey = load_pem_private_key(priv_data, password=None, backend=default_backend())
        print "Loaded private key..."

	def decryptSymKey(self, ctKey):
		from cryptography.hazmat.primitives.asymmetric import padding
		from cryptography.hazmat.primitives import hashes

		ptSymKey = self.privKey.decrypt(ctKey,
			padding.OAEP(
				mgf=padding.MGF1(algorithm=hashes.SHA1()),
				algorithm=hashes.SHA1(),
				label=None
        	)
		)
		print ptSymKey
		return ptSymKey

	def encryptTraffic(self, client, msg):
		from cryptography.fernet import Fernet
		f = Fernet(self.symKeyMap[client])
		token = f.encrypt(msg)
		return token

	def decryptTraffic(self, client, token):
		from cryptography.fernet import Fernet
		f = Fernet(self.symKeyMap[client])
		msg = f.decrypt(token)
		return msg
		
	def getname(self, client):
		return self.clientmap[client][1]

	def getHelp(self, client):
		helpCmd = '''
			LIST OF COMMANDS:
			
			help - provide list of all chat commands
			list - provide list of all users online
			send user message- send a message to a user on the network
			broadcast message- send a message to everyone on the network.
			kick user password - as admin kick a user.
		'''
		
		for o in self.outputs:
			if o == client:
				eHelpCmd = self.encryptTraffic(client, helpCmd)
				o.send(eHelpCmd)
				
	def getListOfUsers(self, client):
		users = []
		for keyClient in self.clientmap:
			clientInfo = self.clientmap[keyClient]
			users.append(clientInfo[1])
		listOfUsers = 'Online Users ' + str(users)
		for o in self.outputs:
			if o == client:
				eListOfUsers = self.encryptTraffic(client, listOfUsers)
				o.send(eListOfUsers)
				
	def sendMessageToAll(self, client, arguments):
		for o in self.outputs:
			if o != client: #send to everyone except ourselves.
				msg = ''
				for arg in arguments:
					msg += (arg + ' ')
				p = '{}: '.format(self.getname(client))
				broadcast = p + msg
				eBroadcast = self.encryptTraffic(client, broadcast)
				o.send(eBroadcast)
				
	def sendMessage(self, client, arguments):
		if len(arguments) < 2:
			e = 'To send a message you need two arguments. A user, and a message'
			self.errorMessage(client, '', e)
			return
		for key in self.clientmap:
			user = self.clientmap[key][1]
			if user == arguments[0]:
				msg = ''
				for arg in range(1, len(arguments)):
					msg += (arguments[arg] + ' ')
				for o in self.outputs:
					if o == key:
						p = '{}: '.format(self.getname(client))
						idvMsg = p + msg
						eIdvMsg = self.encryptTraffic(client, msg)
						o.send(eIdvMsg)
						return
		e = 'User {} is not connected.'.format(arguments[0])
		self.errorMessage(client, '', e)
		
	def adminKick(self, client, arguments):
		if len(arguments) < 2:
			e = 'To kick a user you must specify the user and enter the password'
			self.errorMessage(client, '', e)
			return
		if arguments[1] != self.adminPassword:
			e = 'Invalid password. Unable to kick user'
			self.errorMessage(client, '', e)
			return
		usr = arguments[0]
		for gkey in self.groupmap: #remove user from all groups
				if usr in self.groupmap[gkey]:
					self.groupmap[gkey].remove(usr)
		for key in self.clientmap:
			usr = self.clientmap[key][1]
			if usr == arguments[0]:
				for o in self.outputs:
					if o == key:
						kickMsg = 'You are the weakest link...goodbye.'
						eKickMsg = self.encryptTraffic(client, kickMsg)
						o.send(eKickMsg)
						self.inputs.remove(o)
						self.outputs.remove(o)
						self.clientmap.pop(key)
						key.close()
						o.close()
						return
						
	def errorMessage(self, client, data, errorMsg=''):
		error = '"{}" is not a valid command. Press help for valid commands.'.format(data)
		if errorMsg != '':
			error = errorMsg
		for o in self.outputs:
			if o == client:
				eError = self.encryptTraffic(client, error)	
				o.send(eError)
				
	def isUserOnline(self, userName):
		for key in self.clientmap:
			usr = self.clientmap[key][1]
			if usr == userName:
				return True
		return False
			   
	def handleClientData(self, data, client):
		instructions = data.split(' ')
		cmd = instructions[0].strip()
		arguments = []
		if len(instructions) > 1:
			for i in range(1, len(instructions)):
				arguments.append(instructions[i])
		if cmd == 'help': self.getHelp(client); return;
		if cmd == 'list': self.getListOfUsers(client); return;
		if cmd == 'broadcast': self.sendMessageToAll(client, arguments); return;
		if cmd == 'send': self.sendMessage(client, arguments); return;
		if cmd == 'kick': self.adminKick(client, arguments); return;
		self.errorMessage(client, data)
	
	def serve(self):

		self.loadRSAprivKey()

		self.inputs = [self.server,sys.stdin]
		self.outputs = []

		running = 1

		while running:

			try:
				inputready,outputready,exceptready = select.select(self.inputs, self.outputs, [])
			except select.error, e:
				break
			except socket.error, e:
				break

			for s in inputready:

				if s == self.server:
					# handle the server socket
					client, address = self.server.accept()
					
					# Read the login name
					cname = client.recv(self.maxBufSize).split('NAME: ')[1]
					print '{} connected to The Office fanatics chat server from {}'.format(cname, address)
					
					# Compute client name and send back
					self.clients += 1
					client.send('CLIENT: ' + str(address[0]))
					self.inputs.append(client)

					self.clientmap[client] = (address, cname)
					# Send joining information to other clients
					msg = 'Connected a new client'
					for o in self.outputs:
						o.send(msg)
					
					self.outputs.append(client)
			
					ctSymKey = client.recv(self.maxBufSize).split('ctSymKey: ')[1]
					print "Server received symmetric key from {}".format(cname)	
					ptSymKey = self.decryptSymKey(ctSymKey)
					print "Decrypted symmetric key from {}".format(cname)
					self.symKeyMap[client] = ptSymKey

					client.send('Server now communicating with {} using symmetric key...'.format(cname))

				elif s == sys.stdin:
					# handle standard input
					junk = sys.stdin.readline()
					running = 0
				else:
					# handle all other sockets
					try:
						# receive encrypted data from client
						eData = s.recv(self.maxBufSize)
						print eData
						if eData:
							data = self.decryptTraffic(s, eData)
							self.handleClientData(data, s)
						else:
							#print 'chatserver: %d hung up' % s.fileno()
							self.clients -= 1
							s.close()
							self.inputs.remove(s)
							self.outputs.remove(s)

							# Send client leaving information to others
							msg = 'A client has hung up'
							usr = self.clientmap[s][1]
							for key in self.groupmap:
								if usr in self.groupmap[key]:
									self.groupmap[key].remove(usr)
							self.clientmap.pop(s) 
							for o in self.outputs:
								o.send(msg)
								
					except socket.error, e:
						self.inputs.remove(s)
						self.outputs.remove(s)

		self.server.close()

'''
getPort is a helper method for error handling of raw input for port nums
'''	
def getPort(argsFromCommandLine):
	
	if len(argsFromCommandLine) == 2:
		port = int(argsFromCommandLine[1])

	else:
		port = raw_input('port: ')

		# check for non-characters and negative or large port numbers
		while not port.isdigit() or int(port) < 0 or int(port) > 65536:
			print "Invalid Port Number, try again."
			port = raw_input('port: ')

		# cast port only when know it's valid
		port = int(port)

	return port

def main(argv):

	port = getPort(argv)
	s = serverTCPchat(port)
	s.serve()

if __name__ == "__main__":
	main(sys.argv)

