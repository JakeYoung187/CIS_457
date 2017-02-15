import java.io.*; // input output functions
import java.net.*; // networking functions
import java.nio.*; // non-blocking io / new io
import java.nio.channels.*; // where socket functions live

import java.util.*; // need the Iterator

class udpserver {

	public static void main(String args[]) {

		try {

			DatagramChannel c = DatagramChannel.open();
		
			// can do more than what we use for
			// gives set of channels to look at
			// do any of these channels have data available
			// we are underutilizing as we just have one channel
			Selector s = Selector.open();

			// make non-blocking
			// every call to recv/read
			// says whether data is available or not
			// most instances not what want
			c.configureBlocking(false);
	
			// have selector and channel
			// associate channel with selector
			// check if data available to read
			// can also check read/write/connect/accept
			// two param and three param version
			c.register(s, SelectionKey.OP_READ);

			c.bind(new InetSocketAddress(9876));

			while(true) {
				
				// since recv non-blocking, so we need to block here
				// number of channels in selector we've selected
				// 5000 param version checks for timeout
				// units are milliseconds
				int n = s.select(5000);

				// must have timed out
				if (n == 0) {
					System.out.println("Got a timeout");
				}
				else {
					// need to iterate over channels selected
					// silly in our case as we only have one channel
					// but still necessary
					Iterator i = s.selectedKeys().iterator();
					while (i.hasNext()) {
						// use iterator to get next channel
						SelectionKey k = (SelectionKey)i.next();
						// get channel from selection
						DatagramChannel myChannel =  (DatagramChannel)k.channel();
						ByteBuffer buffer = ByteBuffer.allocate(4896);
						SocketAddress clientaddr = c.receive(buffer);
						String message = new String(buffer.array());
						System.out.println(message);
						
						// need iterator to call remove
						// if we don't call remove, selector 
						// always thinks available to read
						i.remove();
					}
				}
			}
		}
		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
