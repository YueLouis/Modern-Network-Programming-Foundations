import socket
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UDPChatClient:
    def __init__(self, nickname, server_host='localhost', server_port=8888):
        self.nickname = nickname
        self.server_addr = (server_host, server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def receive_messages(self):
        """Receive messages from server in separate thread"""
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"\n{message}")
                print(f"[{self.nickname}]: ", end='', flush=True)
            except Exception as e:
                logger.error(f"Error receiving message: {str(e)}")
                break
    
    def run(self):
        """Main client loop"""
        # Send nickname to register
        self.socket.sendto(self.nickname.encode('utf-8'), self.server_addr)
        
        # Start receive thread
        recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
        recv_thread.start()
        
        # Send messages from user input
        print(f"Connected as '{self.nickname}'. Type messages to send (Ctrl+C to quit):")
        try:
            while True:
                message = input(f"[{self.nickname}]: ")
                if message.strip():
                    self.socket.sendto(message.encode('utf-8'), self.server_addr)
        except KeyboardInterrupt:
            print("\nDisconnecting...")
        finally:
            self.socket.close()

def main():
    nickname = input("Enter your nickname: ").strip()
    if not nickname:
        nickname = "Anonymous"
    
    client = UDPChatClient(nickname)
    client.run()

if __name__ == "__main__":
    main()
