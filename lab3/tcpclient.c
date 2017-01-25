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
	struct sockaddr_in serveraddr;

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
	// 127.0.0.1 is loopback address and returns back to same computer
	serveraddr.sin_addr.s_addr=inet_addr("127.0.0.1");

	// takes socket and address and permanently associates them together
	// make sure there is someone actually listening at that address
	// (send packet over network to make sure someone actually responds)
	// -- if noone there gives error
	// params - socket, address, length of address
	int e = connect(sockfd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	if (e < 0) {
		printf("There was an error connecting\n");
		return 1;
	}

	// Send data over socket
	printf("Enter a message: ");
	char line[5000];
	fgets(line, 5000, stdin);

	// don't need to give address because socket already associated 
	// from connect -- n+1 is for null char at end
	// use strlen only for strings
	// IMPORTANT: only thing we can send over socket is array of chars
	// not that big of a deal, because anything we want we use memcpy
	// to copy into char array
	send(sockfd, line, strlen(line)+1, 0);

	// close the socket
	close(sockfd);

	return 0;
}
