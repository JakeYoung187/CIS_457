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

	struct sockaddr_in serveraddr;

	serveraddr.sin_family=AF_INET;
	serveraddr.sin_port=htons(9876);
	serveraddr.sin_addr.s_addr=inet_addr("127.0.0.1");


	// UDP doesn't "connect"
	// UDP will happily send even if nobody listening
	/*int e = connect(sockfd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	if (e < 0) {
		printf("There was an error connecting\n");
		return 1;
	}*/

	printf("Enter a message: ");
	char line[5000];
	fgets(line, 5000, stdin);

	// send to sendto (two add args), specify address packet should go to now
	sendto(sockfd, line, strlen(line)+1, 0, (struct sockaddr*)&serveraddr, sizeof(serveraddr));

	close(sockfd);

	return 0;
}
