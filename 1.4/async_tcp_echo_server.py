#!/usr/bin/env python3
"""
Lab 1.4: Async TCP Echo Server
Convert Lab 1.1 to async version using asyncio.start_server()

Features:
- Handle 100+ concurrent connections
- Async I/O operations
- Connection timeout (30s idle)
- Graceful shutdown
- Metrics tracking
"""

import asyncio
import sys
from datetime import datetime


class AsyncEchoServer:
    """Async TCP Echo Server with metrics"""
    
    def __init__(self, host='0.0.0.0', port=9999, timeout=30):
        self.host = host
        self.port = port
        self.idle_timeout = timeout
        self.active_connections = 0
        self.total_requests = 0
        self.bytes_received = 0
        self.server = None
    
    async def handle_client(self, reader, writer):
        """
        Handle single client connection asynchronously
        With 30s idle timeout
        """
        addr = writer.get_extra_info('peername')
        self.active_connections += 1
        
        print(f"[{self._timestamp()}] ✅ Client connected: {addr} "
              f"(Active: {self.active_connections})")
        
        try:
            while True:
                try:
                    # Read with timeout for idle connection detection
                    data = await asyncio.wait_for(
                        reader.read(1024),
                        timeout=self.idle_timeout
                    )
                    
                    if not data:
                        break
                    
                    message = data.decode('utf-8', errors='replace').strip()
                    self.total_requests += 1
                    self.bytes_received += len(data)
                    
                    print(f"[{self._timestamp()}] 📥 {addr}: {message} "
                          f"(Request #{self.total_requests})")
                    
                    # Echo back
                    response = f"ECHO: {message}".encode('utf-8')
                    writer.write(response)
                    await writer.drain()
                    
                    print(f"[{self._timestamp()}] 📤 Echo sent to {addr}")
                
                except asyncio.TimeoutError:
                    print(f"[{self._timestamp()}] ⏱️  Timeout: {addr} idle >{self.idle_timeout}s")
                    break
        
        except Exception as e:
            print(f"[{self._timestamp()}] ❌ Error with {addr}: {e}")
        
        finally:
            self.active_connections -= 1
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            
            print(f"[{self._timestamp()}] 🔌 Disconnected: {addr} "
                  f"(Active: {self.active_connections})")
    
    async def print_metrics_periodic(self):
        """Periodically print server metrics (every 10 seconds)"""
        while True:
            try:
                await asyncio.sleep(10)
                self.print_metrics()
            except asyncio.CancelledError:
                break
    
    def print_metrics(self):
        """Print current server metrics"""
        print(f"\n[{self._timestamp()}] 📊 Server Metrics:")
        print(f"   ├─ Total Requests: {self.total_requests}")
        print(f"   ├─ Active Connections: {self.active_connections}")
        print(f"   └─ Bytes Received: {self.bytes_received / 1024:.1f} KB")
    
    async def start(self):
        """Start server and handle graceful shutdown"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )
            
            print(f"\n{'='*60}")
            print(f"🚀 Async Echo Server Started!")
            print(f"   Host: {self.host}")
            print(f"   Port: {self.port}")
            print(f"   Idle Timeout: {self.idle_timeout}s")
            print(f"   Can handle 100+ concurrent connections")
            print(f"{'='*60}\n")
            
            # Start metrics printer
            metrics_task = asyncio.create_task(self.print_metrics_periodic())
            
            async with self.server:
                await self.server.serve_forever()
        
        except KeyboardInterrupt:
            pass
        except OSError as e:
            print(f"❌ Failed to start server: {e}")
            sys.exit(1)
        finally:
            print(f"\n[{self._timestamp()}] 🛑 Shutting down...")
            self.print_metrics()
            print(f"[{self._timestamp()}] ✓ Server stopped")
    
    @staticmethod
    def _timestamp():
        """Return formatted timestamp"""
        return datetime.now().strftime("%H:%M:%S")


async def main():
    """Main entry point"""
    server = AsyncEchoServer(host='0.0.0.0', port=9999, timeout=30)
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Server shutdown")
