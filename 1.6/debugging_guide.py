"""
Lab 1.6: Debugging Guide & AI Prompts

This document provides prompts to use with AI (ChatGPT, Gemini, Claude) 
to debug and optimize the buggy server.
"""

DEBUGGING_PROMPTS = {
    "bug_identification": """
I have an async TCP server that crashes after ~5 connections. Here's the code:

[PASTE buggy_server.py HERE]

What are the bugs in this code? Why does it crash?
""",
    
    "memory_leak": """
My async server has a memory leak. The process memory keeps growing.
Looking at this code:

[PASTE buggy_server.py HERE]

1. Why is there a memory leak?
2. What's the issue with self.clients list?
3. How should I fix it?
""",
    
    "connection_handling": """
This async server doesn't properly handle client disconnections:

[PASTE buggy_server.py HERE]

1. What's wrong with the connection cleanup?
2. Why is writer.close() missing?
3. How do I implement graceful shutdown?
""",
    
    "optimization": """
How can I optimize this async server to handle 10,000+ concurrent connections?

[PASTE fixed_server.py HERE]

1. Should I use uvloop?
2. What's the difference between asyncio and uvloop?
3. How do I implement connection pooling?
4. What other optimizations would help?
""",
    
    "uvloop_usage": """
How do I use uvloop to improve performance of my async server?

Can you show me:
1. How to install uvloop
2. How to integrate it with asyncio
3. Performance comparison: asyncio vs uvloop
""",
}

KEY_BUGS_TO_IDENTIFY = {
    "Bug 1: Unbounded Client List": {
        "location": "self.clients.append(...)",
        "issue": "Clients never removed even after disconnection",
        "impact": "Memory leak - accumulates closed connections",
        "fix": "Use set() and properly track/remove clients"
    },
    
    "Bug 2: Unbounded Request Queue": {
        "location": "self.request_queue.append(...)",
        "issue": "Queue grows indefinitely, never processed",
        "impact": "Memory grows over time, eventual OOM crash",
        "fix": "Use collections.deque with maxlen parameter"
    },
    
    "Bug 3: Missing Error Handling": {
        "location": "message = data.decode('utf-8').upper()",
        "issue": "No try/except for decoding errors",
        "impact": "Crashes on non-UTF8 data, crashes server",
        "fix": "Wrap in try/except, handle gracefully"
    },
    
    "Bug 4: Resources Not Released": {
        "location": "finally block missing writer.close()",
        "issue": "Connection not properly closed",
        "impact": "File descriptor leak, limits max connections",
        "fix": "Add writer.close() and await writer.wait_closed()"
    },
    
    "Bug 5: No Idle Timeout": {
        "location": "No asyncio.wait_for() call",
        "issue": "Hung connections never detected",
        "impact": "Slow accumulation of zombie connections",
        "fix": "Use asyncio.wait_for(reader.read(), timeout=30)"
    },
}

OPTIMIZATION_TECHNIQUES = {
    "1. Use uvloop": {
        "description": "Drop-in replacement for asyncio event loop",
        "benefit": "2-4x performance improvement",
        "code": """
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
""",
        "install": "pip install uvloop"
    },
    
    "2. Bounded Queues": {
        "description": "Prevent unbounded memory growth",
        "code": """
from collections import deque
self.queue = deque(maxlen=1000)  # Max 1000 items
"""
    },
    
    "3. Connection Timeouts": {
        "description": "Detect and close idle connections",
        "code": """
try:
    data = await asyncio.wait_for(
        reader.read(1024),
        timeout=30.0  # 30 second timeout
    )
except asyncio.TimeoutError:
    break  # Close connection
"""
    },
    
    "4. Resource Limits": {
        "description": "Limit max concurrent connections",
        "code": """
class Server:
    def __init__(self, max_connections=10000):
        self.max_connections = max_connections
        self.active_clients = set()
    
    async def handle_client(self, reader, writer):
        if len(self.active_clients) >= self.max_connections:
            writer.close()
            return
        # ... handle client
"""
    },
    
    "5. Proper Cleanup": {
        "description": "Always close resources properly",
        "code": """
try:
    # Handle client
except Exception as e:
    logger.error(f"Error: {e}")
finally:
    try:
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        logger.warning(f"Close error: {e}")
"""
    },
}

PERFORMANCE_BENCHMARKING = """
Compare buggy vs fixed server:

1. Start buggy_server.py:
   python 1.6/buggy_server.py

2. In another terminal, run benchmark:
   python ../1.4/benchmark_server.py localhost:9995 50 20

3. Observe:
   - Does it crash after ~5 connections?
   - Memory usage spike?
   - Error messages?

4. Now test fixed_server.py:
   python 1.6/fixed_server.py
   python ../1.4/benchmark_server.py localhost:9996 100 50

5. Compare results:
   - buggy_server: crashes, high latency
   - fixed_server: stable, low latency
"""

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Lab 1.6: AI-Enhanced Debugging Guide")
    print("="*70)
    
    print("\n1. BUG IDENTIFICATION")
    print("-" * 70)
    print("Use this prompt with AI:")
    print(DEBUGGING_PROMPTS["bug_identification"])
    
    print("\n2. KEY BUGS TO IDENTIFY")
    print("-" * 70)
    for bug, details in KEY_BUGS_TO_IDENTIFY.items():
        print(f"\n{bug}")
        for key, value in details.items():
            print(f"  {key}: {value}")
    
    print("\n3. OPTIMIZATION TECHNIQUES")
    print("-" * 70)
    for num, (technique, details) in enumerate(OPTIMIZATION_TECHNIQUES.items(), 1):
        print(f"\n{technique}")
        for key, value in details.items():
            if key != "code":
                print(f"  {key}: {value}")
    
    print("\n4. BENCHMARKING")
    print("-" * 70)
    print(PERFORMANCE_BENCHMARKING)
    
    print("="*70 + "\n")
