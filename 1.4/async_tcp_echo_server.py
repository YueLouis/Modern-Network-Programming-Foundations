import asyncio
import logging
from datetime import datetime
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AsyncEchoServer:
    def __init__(self, host='localhost', port=9999, idle_timeout=30):
        self.host = host
        self.port = port
        self.idle_timeout = idle_timeout
        
        # Metrics
        self.total_requests = 0
        self.active_connections = 0
        self.server = None
        self.shutdown_event = asyncio.Event()
    
    async def handle_client(self, reader, writer):
        """Handle async client connection with timeout"""
        client_addr = writer.get_extra_info('peername')
        self.active_connections += 1
        
        logger.info(f"Client connected: {client_addr[0]}:{client_addr[1]} "
                   f"(Active: {self.active_connections})")
        
        try:
            while not self.shutdown_event.is_set():
                try:
                    # Read with timeout for idle connection detection
                    data = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=self.idle_timeout
                    )
                    
                    if not data:
                        logger.info(f"Client {client_addr[0]} closed connection")
                        break
                    
                    message = data.decode('utf-8').strip()
                    self.total_requests += 1
                    logger.info(f"Request #{self.total_requests} from {client_addr[0]}: {message}")
                    
                    # Echo back with prefix
                    response = f"ECHO: {message}".encode('utf-8')
                    writer.write(response)
                    await writer.drain()
                    logger.info(f"Sent to {client_addr[0]}: {response.decode()}")
                
                except asyncio.TimeoutError:
                    logger.warning(f"Client {client_addr[0]} idle timeout ({self.idle_timeout}s)")
                    break
        
        except Exception as e:
            logger.error(f"Error handling client {client_addr[0]}: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
            self.active_connections -= 1
            logger.info(f"Connection closed with {client_addr[0]}. "
                       f"Active: {self.active_connections}")
    
    async def print_metrics(self):
        """Periodically print server metrics"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(10)
                logger.info(f"=== METRICS === Total Requests: {self.total_requests} | "
                           f"Active Connections: {self.active_connections}")
            except asyncio.CancelledError:
                break
    
    def handle_signal(self, sig):
        """Handle shutdown signal"""
        logger.info(f"Received signal {sig}. Starting graceful shutdown...")
        self.shutdown_event.set()
    
    async def run(self):
        """Start server with graceful shutdown"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"Async Echo Server listening on {self.host}:{self.port}")
        logger.info(f"Idle timeout: {self.idle_timeout}s | Max concurrent: 100+")
        
        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self.handle_signal, sig)
        
        # Start metrics printer
        metrics_task = asyncio.create_task(self.print_metrics())
        
        async with self.server:
            try:
                # Serve until shutdown
                while not self.shutdown_event.is_set():
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Server error: {str(e)}")
            finally:
                metrics_task.cancel()
                try:
                    await metrics_task
                except asyncio.CancelledError:
                    pass
                
                logger.info(f"Server shutdown. Final metrics: "
                           f"Total Requests: {self.total_requests}, "
                           f"Active Connections: {self.active_connections}")

async def main():
    server = AsyncEchoServer(host='localhost', port=9999, idle_timeout=30)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
