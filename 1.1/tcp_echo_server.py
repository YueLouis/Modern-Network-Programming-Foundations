import socket
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_client(client_socket, client_address):
    """Handle client connection and echo messages back"""
    logger.info(f"Client connected from {client_address[0]}:{client_address[1]}")
    
    try:
        while True:
            # Receive message from client
            data = client_socket.recv(1024).decode('utf-8')
            
            if not data:
                logger.info(f"Client {client_address[0]}:{client_address[1]} disconnected")
                break
            
            message = data.strip()
            logger.info(f"Received from {client_address[0]}: {message}")
            
            # Handle special commands
            if message.upper() == "TIME":
                response = f"SERVER TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                # Echo back with prefix
                response = f"ECHO: {message}"
            
            # Send response back to client
            client_socket.send(response.encode('utf-8'))
            logger.info(f"Sent to {client_address[0]}: {response}")
            
    except Exception as e:
        logger.error(f"Error handling client {client_address[0]}: {str(e)}")
    finally:
        client_socket.close()
        logger.info(f"Connection closed with {client_address[0]}:{client_address[1]}")

def main():
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to port 9999
    PORT = 9999
    server_socket.bind(('localhost', PORT))
    
    # Listen for incoming connections
    server_socket.listen(1)
    logger.info(f"TCP Echo Server listening on port {PORT}...")
    
    try:
        while True:
            # Accept client connection
            client_socket, client_address = server_socket.accept()
            
            # Handle client (sequential, one at a time)
            handle_client(client_socket, client_address)
            
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        server_socket.close()
        logger.info("Server closed")

if __name__ == "__main__":
    main()
