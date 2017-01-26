import java.io.*; // input output functions
import java.net.*; // networking functions
import java.nio.*; // non-blocking io / new io
import java.nio.channels.*; // where socket functions live

class tcpserver {

	public static void main(String args[]) {

		// everything in try catch block
		// because everything can throw io exception
		// don't do for bigger programs
		try {
			// server side in java different than client side
			ServerSocketChannel c = ServerSocketChannel.open();
			
			// connect port
			c.bind(new InetSocketAddress(9876));

			while(true) {
			
				// serial accept from client
				SocketChannel sc = c.accept();

				// create byte buffer of certain size that is empty
				ByteBuffer buffer = ByteBuffer.allocate(4896);

				// receive into that buffer
				sc.read(buffer);
			
				// convert contents of byte buffer into string
				// convert to byte array first
				String message = new String(buffer.array());

				System.out.println(message);

				sc.close();

			}
		}

		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
