import socket
import logging
from threading import Thread, Lock

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UDPChatServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        # Dictionary to store connected clients: (ip, port) -> nickname
        self.clients = {}
        self.clients_lock = Lock()
        
        logger.info(f"UDP Chat Server listening on {self.host}:{self.port}")
    
    def broadcast(self, message, sender_addr=None):
        """Send message to all clients except sender"""
        with self.clients_lock:
            for client_addr in self.clients:
                if client_addr != sender_addr:
                    try:
                        self.socket.sendto(message.encode('utf-8'), client_addr)
                    except Exception as e:
                        logger.error(f"Failed to send to {client_addr}: {str(e)}")
    
    def run(self):
        """Main server loop"""
        try:
            while True:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode('utf-8').strip()
                
                # Register new user
                if addr not in self.clients:
                    # Extract nickname from first message
                    parts = message.split(':', 1)
                    nickname = parts[0] if len(parts) > 0 else f"User_{addr[0]}_{addr[1]}"
                    
                    with self.clients_lock:
                        self.clients[addr] = nickname
                    
                    logger.info(f"User '{nickname}' joined from {addr[0]}:{addr[1]}")
                    self.broadcast(f"[SERVER] '{nickname}' joined the chat", addr)
                else:
                    nickname = self.clients[addr]
                    logger.info(f"Message from {nickname} ({addr[0]}): {message}")
                    self.broadcast(f"{nickname}: {message}", addr)
        
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.socket.close()

def main():
    server = UDPChatServer()
    server.run()

if __name__ == "__main__":
    main()
