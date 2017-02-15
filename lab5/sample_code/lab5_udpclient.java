import java.io.*; // input output functions
import java.net.*; // networking functions
import java.nio.*; // non-blocking io / new io
import java.nio.channels.*; // where socket functions live

class udpclient {

	public static void main(String args[]) {
		
		try {
			// change Socket to DataGram
			DatagramChannel dc = DatagramChannel.open();

			// udp doesn't connect
			//sc.connect(new InetSocketAddress("127.0.0.1", 9876));

			Console cons = System.console();
			String m = cons.readLine("Enter your message: ");
			ByteBuffer buf = ByteBuffer.wrap(m.getBytes());
	
			// send to specific addr instead of write
			//sc.write(buf);
			dc.send(buf, new InetSocketAddress("127.0.0.1", 9876));

			dc.close();

		}

		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
