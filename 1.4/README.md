# Lab 1.4: Async Network Applications (60 minutes)

## Objective
Convert Lab 1.1 TCP server to async version using `asyncio`

## Why Async?
- **Threading bottleneck**: ~100-200 concurrent connections
- **Async strength**: 1000+ concurrent connections on single thread
- **Memory efficient**: ~50KB per connection vs ~8MB with threads

## Theory

### Asyncio Event Loop
```
Event Loop: Vòng lặp chính xử lý tất cả coroutines
│
├─ Task 1: I/O đợi (Socket) → Tạm dừng
├─ Task 2: Xử lý dữ liệu → Chạy
├─ Task 3: I/O đợi (Write) → Tạm dừng
└─ Task 4: Xử lý dữ liệu → Chạy
│
└─ Quay lại Task 1: I/O xong → Chạy
```

### Key Async Concepts
1. **await** - "đợi I/O xong rồi tiếp tục"
2. **async def** - hàm coroutine (có thể tạm dừng)
3. **asyncio.create_task()** - chạy async function không chờ

## In-Class Tasks

### Task 1: Write Async TCP Echo Server
Create: `async_tcp_echo_server.py`

```python
import asyncio

async def handle_client(reader, writer):
    """Handle single client connection asynchronously"""
    addr = writer.get_extra_info('peername')
    print(f"[+] Client connected: {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:  # Client closed connection
                break
            
            print(f"[{addr}] Received: {data.decode()}")
            
            writer.write(b"ECHO: " + data)
            await writer.drain()  # Wait until write buffer is flushed
    
    except Exception as e:
        print(f"[-] Error with {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"[-] Client disconnected: {addr}")

async def main():
    """Start async server"""
    server = await asyncio.start_server(
        handle_client, 
        '127.0.0.1', 
        9999
    )
    
    addr = server.sockets[0].getsockname()
    print(f"🚀 Async Echo Server listening on {addr[0]}:{addr[1]}")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Server shutdown")
```

### Task 2: Benchmark - Compare Performance
Create: `benchmark_server.py`

Test both threading and async versions:
```bash
# Terminal 1: Run async server
python async_tcp_echo_server.py

# Terminal 2: Run benchmark
python benchmark_server.py
```

Use Apache Bench or simple Python stress test:
```python
import socket
import time
import threading

def stress_test(num_clients=100):
    """Send requests from multiple clients"""
    def client():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 9999))
            s.send(b'test message')
            response = s.recv(1024)
            s.close()
            return True
        except:
            return False
    
    start = time.time()
    threads = []
    
    for _ in range(num_clients):
        t = threading.Thread(target=client)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start
    print(f"✅ {num_clients} requests in {elapsed:.2f}s")
    print(f"📊 Throughput: {num_clients/elapsed:.0f} req/sec")
```

## Performance Comparison

### Benchmark Results (Typical)
```
Threading Version (Lab 1.1):
- 100 concurrent clients: ✅
- 500 concurrent clients: ⚠️ Slow (memory: ~400MB)
- 1000 concurrent clients: ❌ Crashes

Async Version (Lab 1.4):
- 100 concurrent clients: ✅✅ Fast (memory: ~5MB)
- 500 concurrent clients: ✅✅ Fast (memory: ~25MB)
- 1000+ concurrent clients: ✅✅ Very Fast (memory: ~50MB)
```

## Homework Tasks (Due Next Class)

### Task 1: Add Connection Timeout
```python
async def handle_client_with_timeout(reader, writer):
    """Handle client with 30s idle timeout"""
    try:
        while True:
            data = await asyncio.wait_for(
                reader.read(1024),
                timeout=30.0  # 30 seconds timeout
            )
            if not data:
                break
            writer.write(b"ECHO: " + data)
            await writer.drain()
    
    except asyncio.TimeoutError:
        print("[-] Client timeout (idle 30s)")
    finally:
        writer.close()
        await writer.wait_closed()
```

### Task 2: Graceful Shutdown
```python
async def main_with_shutdown():
    """Server with graceful shutdown"""
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 9999
    )
    
    async with server:
        # Graceful shutdown on Ctrl+C
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Shutting down gracefully...")
            # Close all connections
            server.close()
            await server.wait_closed()
            print("[✓] Server stopped")
```

### Task 3: Add Metrics
```python
class ServerMetrics:
    """Track server performance metrics"""
    def __init__(self):
        self.total_requests = 0
        self.active_connections = 0
        self.bytes_received = 0
    
    def request_received(self, size):
        self.total_requests += 1
        self.bytes_received += size
    
    def connection_opened(self):
        self.active_connections += 1
    
    def connection_closed(self):
        self.active_connections -= 1
    
    def print_stats(self):
        print(f"""
        📊 Server Statistics:
        ├─ Total Requests: {self.total_requests}
        ├─ Active Connections: {self.active_connections}
        └─ Bytes Received: {self.bytes_received / 1024:.1f} KB
        """)

# Use in handler:
metrics = ServerMetrics()

async def handle_client(reader, writer):
    metrics.connection_opened()
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            metrics.request_received(len(data))
            # ... echo logic
    finally:
        metrics.connection_closed()
```

## Evaluation Rubric
- **Async implementation**: 60% 
  - ✅ Using asyncio.start_server()
  - ✅ Async handle_client coroutine
  - ✅ Proper await usage
  
- **Performance improvement**: 30%
  - ✅ Handles 100+ concurrent connections
  - ✅ Benchmark results show improvement
  - ✅ Memory efficient
  
- **Code quality**: 10%
  - ✅ Error handling
  - ✅ Clean code
  - ✅ Comments

## Common Issues

### ⚠️ Issue: `RuntimeError: There is no current event loop`
**Solution**: Use `asyncio.run()` instead of creating loop manually

### ⚠️ Issue: Server doesn't respond properly
**Check**: Did you use `await writer.drain()`?

### ⚠️ Issue: Memory keeps growing
**Check**: Are you closing connections properly? Use `writer.close()` + `await writer.wait_closed()`

## References
- Python asyncio docs: https://docs.python.org/3/library/asyncio.html
- Real Python - Async IO: https://realpython.com/async-io-python/
