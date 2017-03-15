# CIS 457 Project 2: UDP Relability File Transfer

[Project Description](http://www.cis.gvsu.edu/~kalafuta/cis457/w17/labs/457prj2.html)

## Usage:

chmod u+x udpclient_part2.py

chmod u+x udpserver_part2.py

### Option 1:
./udpclient_part2.py

./udpserver_part2.py

#### Then provide host, port, filename as raw input

### Option 2:
./udpclient_part2.py hostName portNum

./udpserver_part2.py portNum

#### Then provide filename as raw input

### Example:
./udpclient_part2.py 127.0.0.1 1234

./udpserver_part2.py 1234


#### For specifics on simulating relability conditions (loss, reordering, duplications, and corruption), please see the project description.

### Sample output:

[Sliding Window and Ack/Data Loss](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataLoss.png)

[Ack/Data Reordering](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataReordering.png)

[Ack/Data Duplication](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackDataDuplication.png)

[Ack Corruption](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_ackCorruption.png)

[Data Corruption](https://github.com/adamtwig/CIS_457/blob/master/project2/part2/screenshots/CIS457_Project2_dataCorruption.png)
