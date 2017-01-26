import java.io.*; 
import java.net.*;
import java.nio.*;
import java.nio.channels.*;

// see lab2 for previous documentation

// synchronize to deal with global var issues

class tcpserver {
	public static void main(String args[]) {
		try {
			ServerSocketChannel c = ServerSocketChannel.open();
			c.bind(new InetSocketAddress(9876));
			while(true) {
				SocketChannel sc = c.accept();
				TcpServerThread t = new TcpServerThread(sc);
				t.start();
			}
		}
		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
class TcpServerThread extends Thread {
	SocketChannel sc;
	TcpServerThread(SocketChannel channel) {
		sc = channel;
	}	
	public void run() {
		try {		
			ByteBuffer buffer = ByteBuffer.allocate(4896);
			sc.read(buffer);
			String message = new String(buffer.array());
			System.out.println(message);
			sc.close();
		}
		catch (IOException e) {
			System.out.println("Got an IO Exception");
		}
	}
}
