import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def handle_request(reader, writer):
    """Handle HTTP GET requests"""
    client_addr = writer.get_extra_info('peername')
    
    try:
        # Read HTTP request
        data = await reader.read(1024)
        request = data.decode('utf-8')
        
        if not request:
            return
        
        # Parse request line
        lines = request.split('\r\n')
        request_line = lines[0].split()
        
        logger.info(f"Request from {client_addr[0]}: {request_line}")
        
        if len(request_line) < 2:
            response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
            writer.write(response)
            await writer.drain()
            return
        
        method = request_line[0]
        path = request_line[1]
        
        # Only allow GET
        if method != "GET":
            body = f"<h1>405 Method Not Allowed</h1><p>{method} is not supported</p>"
            response = f"""HTTP/1.1 405 Method Not Allowed\r
Content-Type: text/html; charset=utf-8\r
Content-Length: {len(body)}\r
\r
{body}""".encode('utf-8')
            writer.write(response)
            await writer.drain()
            return
        
        # Route requests
        if path == "/" or path == "/index":
            body = """
            <html>
            <head><title>HTTP Server</title></head>
            <body>
                <h1>Simple HTTP GET Server</h1>
                <ul>
                    <li><a href="/time">Server Time</a></li>
                    <li><a href="/status">Server Status</a></li>
                    <li><a href="/info">Server Info</a></li>
                </ul>
            </body>
            </html>
            """.strip()
        elif path == "/time":
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            body = f"<h1>Server Time</h1><p><strong>{current_time}</strong></p>"
        elif path == "/status":
            body = "<h1>Server Status</h1><p><strong>✓ Running</strong></p>"
        elif path == "/info":
            body = "<h1>Server Info</h1><p>Simple HTTP GET Server - Async Version</p>"
        else:
            body = f"<h1>404 Not Found</h1><p>Path '{path}' does not exist</p>"
        
        # Send response
        response = f"""HTTP/1.1 200 OK\r
Content-Type: text/html; charset=utf-8\r
Content-Length: {len(body)}\r
Connection: close\r
\r
{body}""".encode('utf-8')
        
        writer.write(response)
        await writer.drain()
        logger.info(f"Sent response to {client_addr[0]}: {path}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    PORT = 8080
    server = await asyncio.start_server(handle_request, 'localhost', PORT)
    
    logger.info(f"HTTP Server listening on http://localhost:{PORT}")
    logger.info("Available routes: / , /time , /status , /info")
    
    async with server:
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
