# CIS 457 Project 1: TCP File Transfer

[Project Description](http://www.cis.gvsu.edu/~kalafuta/cis457/w17/labs/457prj1.html)

## Usage:

chmod u+x tcpserver.py

chmod u+x tcpclient.py

### Option 1:
./tcpserver.py

./tcpclient.py

#### Then provide host, port, filename as raw input

### Option 2:

./tcpserver.py portNum

./tcpclient.py hostName portNum

#### Then provide filename as raw input

### Example:

./tcpserver.py 1234

./tcpclient.py 127.0.0.1 1234

### Sample output:

[Sliding Window and Ack/Data Loss](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataLoss.png)

[Ack/Data Reordering](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataReordering.png)

[Ack/Data Duplication](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataDuplication.png)

[Ack Corruption](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackCorruption.png)

[Data Corruption](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_dataCorruption.png)
