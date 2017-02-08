#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char** argv) {

	// change to SOCK_DGRAM
	int sockfd = socket(AF_INET, SOCK_DGRAM,0);

	if (sockfd < 0) {
		printf("There was an error creating the socket\n");
		return 1;
	}

	struct sockaddr_in serveraddr, clientaddr;

	serveraddr.sin_family=AF_INET;
	serveraddr.sin_port=htons(9876);
	serveraddr.sin_addr.s_addr=INADDR_ANY;

	int e = bind(sockfd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	if (e < 0) {
		printf("There was an error binding the address\n");
		return 1;
	}
	
	//listen(sockfd,10);

	while (1) {
		int len = sizeof(clientaddr);
		//int clientsocket = accept(sockfd, (struct sockaddr*)&clientaddr, &len);		
	
		char line[5000];
		int n = recvfrom(sockfd, line, 5000, 0, (struct sockaddr*)&clientaddr, &len);
		printf("Got from the client: %s\n", line);
	}

	// only one socket, so don't want to close
	//close(sockfd);

	return 0;
}
