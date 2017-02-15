#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char** argv) {

	int sockfd = socket(AF_INET, SOCK_DGRAM,0);

	if (sockfd < 0) {
		printf("There was an error creating the socket\n");
		return 1;
	}
	
	// two mems, length of time
	struct timeval timeout;
	// num secs rep by struct
	timeout.tv_sec = 5;
	// num microsecs rep by struct
	timeout.tv_usec = 0;

	// modify socket options
	// arg1: socket file descriptor
	// arg2: select category of options
	// arg3: receive timeout
	// arg4: time val
	// arg5: size of arg4
	setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

	struct sockaddr_in serveraddr, clientaddr;

	serveraddr.sin_family=AF_INET;
	serveraddr.sin_port=htons(9876);
	serveraddr.sin_addr.s_addr=INADDR_ANY;

	int e = bind(sockfd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	if (e < 0) {
		printf("There was an error binding the address\n");
		return 1;
	}

	while (1) {
		int len = sizeof(clientaddr);
		char line[5000];
		int n = recvfrom(sockfd, line, 5000, 0, (struct sockaddr*)&clientaddr, &len);
		
		// on any error, recv returns -1, otherwise returns num bytes received
		if (n == -1) {
			printf("Timed out while waiting to receive\n");
		}
		else {
			printf("Got from the client: %s\n", line);
		}
	
	}

	return 0;
}
