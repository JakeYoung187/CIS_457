import java.io.*; // input output functions
import java.net.*; // networking functions
import java.nio.*; // non-blocking io / new io
import java.nio.channels.*; // where socket functions live

class tcpclient {

	public static void main(String args[]) {

		// everything in try catch block
		// because everything can throw io exception
		// don't do for bigger programs
		try {
			// creating socket channel
			// essentially, taking role of socket
			SocketChannel sc = SocketChannel.open();

			// ip address and port number
			// similar to connect call in c
			sc.connect(new InetSocketAddress("127.0.0.1", 9876));

			// get some user input to send
			Console cons = System.console();
			String m = cons.readLine("Enter your message: ");

			// only one datatype we can send over socket
			// -- byte buffer (turn string into array of bytes)
			// take array of chars and create byte buffer
			ByteBuffer buf = ByteBuffer.wrap(m.getBytes());
	
			// tell socket channel to write to byte buffer
			// equivalent to send in c
			sc.write(buf);

			// close socket channel
			sc.close();

		}

		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
