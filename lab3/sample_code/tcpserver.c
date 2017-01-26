#include <sys/socket.h>
#include <netinet/in.h> 
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>

// be aware that these are all the same process
// so each thread sees the same global vars
// solution: semaphore/mutex

struct clientinfo {
	struct sockaddr_in addr;
	int socket;
};

void* handleclient(void *arg) {
	struct clientinfo ci = *(struct clientinfo *)arg;
	//int clientsocket = *(int *)arg;
	int clientsocket = ci.socket;
	struct sockaddr_in clientaddr = ci.addr;
	char line[5000];
	int n = recv(clientsocket, line, 5000, 0);
	printf("Got from the client: %s\n", line);
	close(clientsocket);
}

int main(int argc, char** argv) {
	int sockfd = socket(AF_INET, SOCK_STREAM,0);
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
	listen(sockfd,10);
	while (1) {
		int len = sizeof(clientaddr);
		int clientsocket = accept(sockfd, (struct sockaddr*)&clientaddr, &len);
		struct clientinfo ci;
		ci.socket = clientsocket;
		ci.addr = clientaddr;	
		pthread_t child; // thread handle, reference thread
		// 1. pointer to thread, 2. pthread attrs, 
		// 3. function to run, 4. void pointer to args
		//pthread_create(&child, NULL, handleclient, &clientsocket);
		pthread_create(&child, NULL, handleclient, &ci);
		// don't care about return value, but want to clean up memory
		pthread_detach(child);	
	}
	return 0;
}
