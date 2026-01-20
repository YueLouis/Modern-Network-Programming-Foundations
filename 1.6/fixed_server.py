"""
Lab 1.6.2: Fixed and Optimized Async Server
Demonstrates fixes for bugs found in buggy_server.py
"""
import asyncio
import logging
from collections import deque
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedAsyncServer:
    def __init__(self, port=9996, max_connections=100, queue_size=1000):
        self.port = port
        self.max_connections = max_connections
        self.queue_size = queue_size
        
        # FIX 1: Use weak references and proper cleanup
        self.active_clients = set()
        
        # FIX 2: Bounded queue with maxlen
        self.request_queue = deque(maxlen=queue_size)
        
        # Metrics
        self.total_requests = 0
        self.total_connections = 0
        self.start_time = datetime.now()
    
    async def handle_client(self, reader, writer):
        """Fixed handler with proper error handling"""
        client_addr = writer.get_extra_info('peername')
        
        # FIX 1: Track clients properly
        client_id = f"{client_addr[0]}:{client_addr[1]}"
        self.active_clients.add(client_id)
        self.total_connections += 1
        
        logger.info(f"Client connected: {client_id} "
                   f"(Active: {len(self.active_clients)}/{self.max_connections})")
        
        try:
            while True:
                try:
                    # FIX 2: Add timeout to prevent hanging connections
                    data = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=30.0
                    )
                    
                    # FIX 3: Handle empty data gracefully
                    if not data:
                        logger.info(f"Client {client_id} closed connection")
                        break
                    
                    # FIX 4: Proper error handling for malformed data
                    try:
                        message = data.decode('utf-8').upper()
                    except UnicodeDecodeError:
                        logger.warning(f"Invalid UTF-8 from {client_id}")
                        response = b"ERROR: Invalid encoding\n"
                        writer.write(response)
                        await writer.drain()
                        continue
                    
                    # Echo response
                    response = f"ECHO: {message}".encode('utf-8')
                    writer.write(response)
                    await writer.drain()
                    
                    # FIX 2: Use bounded queue
                    self.request_queue.append({
                        'client': client_id,
                        'timestamp': datetime.now().isoformat(),
                        'data_len': len(data)
                    })
                    
                    self.total_requests += 1
                
                except asyncio.TimeoutError:
                    logger.warning(f"Client {client_id} idle timeout")
                    break
        
        except Exception as e:
            logger.error(f"Error handling {client_id}: {str(e)}")
        
        finally:
            # FIX 1: Properly close connection
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.warning(f"Error closing {client_id}: {str(e)}")
            
            # FIX 1: Remove from tracking
            self.active_clients.discard(client_id)
            logger.info(f"Connection closed: {client_id} "
                       f"(Active: {len(self.active_clients)})")
    
    async def print_metrics(self):
        """Periodically print server metrics"""
        while True:
            try:
                await asyncio.sleep(10)
                uptime = (datetime.now() - self.start_time).total_seconds()
                logger.info(f"=== METRICS === "
                           f"Uptime: {uptime:.1f}s | "
                           f"Total Connections: {self.total_connections} | "
                           f"Active: {len(self.active_clients)} | "
                           f"Requests: {self.total_requests} | "
                           f"Queue: {len(self.request_queue)}/{self.queue_size}")
            except asyncio.CancelledError:
                break
    
    async def run(self):
        """Start optimized server"""
        server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            self.port
        )
        
        logger.info(f"Optimized Server listening on port {self.port}")
        logger.info(f"Max connections: {self.max_connections}")
        logger.info(f"Queue size: {self.queue_size}")
        
        # Start metrics task
        metrics_task = asyncio.create_task(self.print_metrics())
        
        async with server:
            try:
                await server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Shutting down...")
            finally:
                metrics_task.cancel()

async def main():
    # Use uvloop for better performance (optional)
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("Using uvloop for improved performance")
    except ImportError:
        logger.info("uvloop not installed. Using standard asyncio")
    
    server = OptimizedAsyncServer(port=9996)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
