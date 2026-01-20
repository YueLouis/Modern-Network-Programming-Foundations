"""
Lab 1.6.1: Buggy Async Server (INTENTIONALLY BUGGY)
This server has several common bugs that cause crashes after ~5 connections

BUGS INTENTIONALLY INCLUDED:
1. Memory leak - not properly closing connections
2. Exception not handled - crashes on malformed data
3. Resource limit - no connection pooling
4. Unbounded queue - accumulates clients indefinitely
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuggyAsyncServer:
    def __init__(self, port=9995):
        self.port = port
        self.clients = []  # BUG: Unbounded list - never clears
        self.request_queue = []  # BUG: Queue grows indefinitely
    
    async def handle_client(self, reader, writer):
        """Buggy handler - causes memory leak"""
        client_addr = writer.get_extra_info('peername')
        self.clients.append((reader, writer))  # BUG: Never removes dead clients
        
        logger.info(f"Client connected: {client_addr[0]} (Total: {len(self.clients)})")
        
        try:
            while True:
                data = await reader.read(1024)
                
                # BUG: No error handling for malformed data
                message = data.decode('utf-8').upper()  # Crashes on bad encoding
                
                # BUG: Exception not caught properly
                response = f"ECHO: {message}".encode('utf-8')
                writer.write(response)
                await writer.drain()
                
                # BUG: Queue never processed
                self.request_queue.append({
                    'client': client_addr,
                    'data': data,
                    'response': response
                })
                
                if len(self.request_queue) > 1000:  # Causes memory spike
                    logger.warning(f"Queue size: {len(self.request_queue)}")
        
        # BUG: Resources not properly released
        finally:
            logger.info(f"Client {client_addr[0]} disconnected")
            # writer is not closed!
            # Missing: writer.close() and await writer.wait_closed()
    
    async def run(self):
        """Start the buggy server"""
        server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            self.port
        )
        
        logger.info(f"Buggy Server running on port {self.port}")
        logger.warning("WARNING: This server has known bugs!")
        
        async with server:
            try:
                await server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Shutting down...")

async def main():
    server = BuggyAsyncServer(port=9995)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
