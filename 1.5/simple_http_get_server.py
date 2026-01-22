"""
Lab 1.5: Simple HTTP GET Server
For testing HTTP traffic analyzer
"""
import socket
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

HOST = '0.0.0.0'
PORT = 8080

def handle_request(client_socket, addr):
    """Handle single HTTP request"""
    try:
        request = client_socket.recv(1024).decode('utf-8')
        logger.info(f"Request from {addr}:")
        logger.info(request.split('\r\n')[0])  # First line only
        
        # Simple HTTP response
        response = """HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head>
    <title>Simple HTTP Server</title>
</head>
<body>
    <h1>Lab 1.5 HTTP Server</h1>
    <p>This is a simple HTTP GET server for testing.</p>
    <p>Request received at: {}</p>
</body>
</html>
""".format(addr)
        
        client_socket.sendall(response.encode('utf-8'))
        
    except Exception as e:
        logger.error(f"Error handling request: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    print("\n" + "="*60)
    print("🌐 Simple HTTP Server Started!")
    print(f"   URL: http://localhost:{PORT}")
    print(f"   Listening on {HOST}:{PORT}")
    print("   Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        while True:
            client, addr = server.accept()
            logger.info(f"Connection from {addr}")
            handle_request(client, addr)
    except KeyboardInterrupt:
        print("\n\n[!] Server stopped")
    finally:
        server.close()

if __name__ == "__main__":
    main()
