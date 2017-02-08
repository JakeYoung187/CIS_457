import java.io.*; // input output functions
import java.net.*; // networking functions
import java.nio.*; // non-blocking io / new io
import java.nio.channels.*; // where socket functions live

class udpserver {

	public static void main(String args[]) {

		try {
			
			// change ServerSocket to Datagram
			DatagramChannel c = DatagramChannel.open();
			
			c.bind(new InetSocketAddress(9876));

			while(true) {
			
				// udp doesn't accept
				//SocketChannel sc = c.accept();

				ByteBuffer buffer = ByteBuffer.allocate(4896);

				// return addr of who sent packet
				SocketAddress clientaddr = c.receive(buffer);
			
				String message = new String(buffer.array());

				System.out.println(message);

				// only one socket, don't close
				//sc.close();

			}
		}

		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
