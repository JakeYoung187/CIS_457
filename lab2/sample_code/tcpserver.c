#include <sys/socket.h>
#include <netinet/in.h> //standard internet protocols
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char** argv) {
	// create socket that communicates over network
	// AF_INET internet socket - standard protocols
	// SOCK_STREAM what type of internet socket
	//  - determine transport layer player (TCP)
	//  anything we send is guaranteed to arrive (SOCK_STREAM)
	int sockfd = socket(AF_INET, SOCK_STREAM,0);

	// chances of error creating socket pretty low
	// too many file descriptors open already...
	if (sockfd < 0) {
		printf("There was an error creating the socket\n");
		return 1;
	}

	// Make an address for the socket to communicate with
	// DIFF: server and client address
	struct sockaddr_in serveraddr, clientaddr;

	// ipv4 address (socket functions are more generic)
	serveraddr.sin_family=AF_INET;

	// port number is how we specific application that should be
	// receiving the data we are sending over the socket
	// when we start up server, listen on certain port number
	// IMPORTANT: make sure to change port number for our code
	// two port numbers involved, OS does one direction
	serveraddr.sin_port=htons(9876);

	// struct inside struct that contains one member
	// text version of address and converts to binary 
	// representation of address
	// special address great for examples and testing
	// DIFF: INADDR_ANY (special constant any address this comp has)
	// ways of making server programs portable
	serveraddr.sin_addr.s_addr=INADDR_ANY;


	// ways of saying this socket and this address go together
	// this the address of our end of socket (connect said remote)
	// if someone is using the port, returns error 
	int e = bind(sockfd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	if (e < 0) {
		printf("There was an error binding the address\n");
		return 1;
	}
	
	// listen for incoming connections
	listen(sockfd,10);

	// infinite loop - crude way of handling multiple clients
	// handles them serially, until the current client is done
	// others wait until current client is done
	// multiple clients at same time is next week lab
	while (1) {
		int len = sizeof(clientaddr);
		// accept a connection from an incoming client
		// returns a different socket (on server side 
		// multiple sockets) one to listen for incoming connections
		// every time we get an incoming connection, we create a
		// new socket -- accept is blocking call (wait until have connection)
		int clientsocket = accept(sockfd, (struct sockaddr*)&clientaddr, &len);		
	
		char line[5000];

		// socket receives a message
		// receive is by default a blocking call
		// if there is nothing here for us to receive, wait
		// until data does arrive
		// n is number of bytes received
		// if negative then error
		int n = recv(clientsocket, line, 5000, 0);
		
		// forgot about null character at end of string
		// fix on client: n+1 characters in original string
		// fix on server: append \0 (null char)
		printf("Got from the client: %s\n", line);
	}

	// close the socket
	close(sockfd);

	return 0;
}
