import socket
import threading
import logging
from queue import Queue

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreadPoolServer:
    def __init__(self, host='localhost', port=9998, max_threads=10):
        self.host = host
        self.port = port
        self.max_threads = max_threads
        self.active_connections = 0
        self.connections_lock = threading.Lock()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        logger.info(f"Multi-threaded TCP Server listening on {self.host}:{self.port}")
        logger.info(f"Max threads: {self.max_threads}")
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        try:
            logger.info(f"Client connected: {client_address[0]}:{client_address[1]} "
                       f"(Active: {self.active_connections})")
            
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                
                if not data:
                    logger.info(f"Client {client_address[0]} disconnected")
                    break
                
                message = data.strip()
                logger.info(f"Received from {client_address[0]}: {message}")
                
                # Echo back with prefix
                response = f"ECHO: {message}"
                client_socket.send(response.encode('utf-8'))
                logger.info(f"Sent to {client_address[0]}: {response}")
        
        except Exception as e:
            logger.error(f"Error handling client {client_address[0]}: {str(e)}")
        finally:
            client_socket.close()
            with self.connections_lock:
                self.active_connections -= 1
            logger.info(f"Connection closed with {client_address[0]}. "
                       f"Active connections: {self.active_connections}")
    
    def run(self):
        """Main server loop"""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                
                with self.connections_lock:
                    if self.active_connections >= self.max_threads:
                        logger.warning(f"Max connections ({self.max_threads}) reached. "
                                      f"Rejecting connection from {client_address[0]}")
                        client_socket.send(b"Server is full. Try again later.")
                        client_socket.close()
                        continue
                    
                    self.active_connections += 1
                
                # Spawn new thread for this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=False
                )
                client_thread.start()
        
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self.server_socket.close()
            logger.info("Server closed")

def main():
    server = ThreadPoolServer(max_threads=10)
    server.run()

if __name__ == "__main__":
    main()
