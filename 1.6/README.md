# Lab 1.6: AI-Enhanced Debugging (60 minutes)

## Objective
Use AI tools (ChatGPT, Gemini) to debug and optimize async servers

## Why AI for Debugging?

Traditional debugging flow:
1. Read error message ❌ (confusing)
2. Search StackOverflow 😅 (time-consuming)
3. Trial and error 🔥 (frustrating)

AI-Enhanced debugging:
1. Paste code + error to ChatGPT/Gemini 🤖
2. Get instant explanation + fixes ⚡
3. Understand root cause 💡
4. Apply optimization suggestions 🚀

## In-Class Tasks

### Task 1: Identify Bugs in Buggy Server

File: `buggy_server.py` (provided with intentional bugs)

**Common bugs to find:**
- ❌ Server crashes after 5 connections
- ❌ Memory leak (connections not closed)
- ❌ Slow response time
- ❌ Missing error handling

### Task 2: Use AI to Debug

**Workflow:**
```
┌─────────────────────────┐
│ 1. Run buggy_server.py  │
│    (observe error)      │
└───────────┬─────────────┘
            │
┌───────────v─────────────┐
│ 2. Copy code + error to │
│    ChatGPT/Gemini       │
│    Prompt: "This async  │
│    server crashes after │
│    5 connections. Why?" │
└───────────┬─────────────┘
            │
┌───────────v─────────────┐
│ 3. Analyze AI response  │
│    (understand issue)   │
└───────────┬─────────────┘
            │
┌───────────v─────────────┐
│ 4. Implement fixes      │
│    (apply changes)      │
└───────────┬─────────────┘
            │
┌───────────v─────────────┐
│ 5. Test with benchmark  │
│    (verify fix works)   │
└─────────────────────────┘
```

### Task 3: Implement Fixes

File: `fixed_server.py`

**Common fixes:**
```python
# ❌ BUG: Not closing connections
async def handle_client_buggy(reader, writer):
    data = await reader.read(1024)
    writer.write(data)
    # Missing: writer.close()

# ✅ FIX: Properly close connections
async def handle_client_fixed(reader, writer):
    try:
        data = await reader.read(1024)
        writer.write(data)
    finally:
        writer.close()
        await writer.wait_closed()
```

### Task 4: Optimize with AI

**Prompt to ChatGPT/Gemini:**
```
"I have this async echo server handling 100s of 
concurrent connections. How can I optimize it for 
10,000 concurrent connections?

Key areas:
1. Connection pooling
2. uvloop (faster event loop)
3. Buffer management
4. Memory optimization"
```

**AI will suggest:**
1. Use `uvloop` - faster asyncio implementation
2. Implement connection pooling
3. Tune buffer sizes
4. Monitor memory usage
5. Use benchmarking tools

## Homework Tasks

### Task 1: Research uvloop

**What is uvloop?**
- Faster implementation of asyncio event loop
- 2-4x faster than standard asyncio
- Drop-in replacement (just import it)

```bash
pip install uvloop
```

```python
import asyncio
import uvloop

# Use uvloop instead of default asyncio
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def main():
    # Your async code here
    pass

asyncio.run(main())
```

**Benchmark:**
```
Standard asyncio:  10,000 req/sec
uvloop:           30,000 req/sec  (3x faster!)
```

### Task 2: Implement Optimizations

```python
import asyncio
import uvloop

class OptimizedAsyncServer:
    """Optimized async server with uvloop"""
    
    def __init__(self):
        # Use uvloop for better performance
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        self.active_connections = 0
        self.connection_pool = []
    
    async def handle_client(self, reader, writer):
        """Optimized handler"""
        self.active_connections += 1
        
        try:
            while True:
                # Read with larger buffer for efficiency
                data = await reader.read(4096)  # Larger buffer
                
                if not data:
                    break
                
                writer.write(b"ECHO: " + data)
                await writer.drain()
        
        finally:
            self.active_connections -= 1
            writer.close()
            await writer.wait_closed()
    
    async def start(self):
        """Start optimized server"""
        server = await asyncio.start_server(
            self.handle_client, '0.0.0.0', 9999
        )
        
        async with server:
            await server.serve_forever()
```

### Task 3: Benchmark Before & After

```python
import time
import asyncio

async def benchmark_original():
    """Benchmark standard asyncio"""
    start = time.time()
    
    # Run test
    # ...
    
    elapsed = time.time() - start
    print(f"Standard asyncio: {elapsed:.2f}s")
    return elapsed

async def benchmark_optimized():
    """Benchmark with uvloop"""
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    start = time.time()
    
    # Run same test
    # ...
    
    elapsed = time.time() - start
    print(f"Optimized with uvloop: {elapsed:.2f}s")
    return elapsed
```

**Expected Results:**
```
Original version:      5.2 seconds
Optimized version:     1.8 seconds
Improvement:           65% faster! 🚀
```

## AI Debugging Checklist

When using AI for debugging:

- [ ] **Provide complete context**
  - ✅ Full error message
  - ✅ Relevant code (not just snippets)
  - ✅ Expected vs actual behavior

- [ ] **Ask specific questions**
  - ✅ "Why does this crash?"
  - ✅ "How do I fix memory leak?"
  - ✅ "What's the best practice here?"

- [ ] **Verify AI suggestions**
  - ✅ Test the fix yourself
  - ✅ Understand why it works
  - ✅ Don't blindly copy-paste

- [ ] **Document the learning**
  - ✅ Note what the bug was
  - ✅ Note how it was fixed
  - ✅ Note why the fix works

## Evaluation Rubric
- **Bug identification**: 30%
  - ✅ Found 3+ bugs in buggy_server.py
  - ✅ Explained each bug clearly

- **AI usage effectiveness**: 30%
  - ✅ Used AI productively
  - ✅ Asked good questions
  - ✅ Verified suggestions

- **Fix implementation**: 30%
  - ✅ All bugs fixed
  - ✅ No new bugs introduced
  - ✅ Code runs without crashes

- **Performance improvement**: 10%
  - ✅ Measurable improvement
  - ✅ Used uvloop correctly
  - ✅ Benchmark results documented

## Example: AI Debugging Session

**You:** "This async echo server crashes after ~5 connections"

**ChatGPT:** "That suggests a resource exhaustion issue. Check:
1. Are you closing connections properly?
2. Do you have exception handling?
3. Is there a file descriptor limit?

Let me see your handler code..."

**You:** [paste code]

**ChatGPT:** "I see the issue! You're not awaiting `wait_closed()`. 
Here's the fix:
```python
finally:
    writer.close()
    await writer.wait_closed()  # <- Add this line
```

Also add try/except for proper cleanup."

**You:** "Thanks! That fixed it. Now testing with 100 connections..."

## Recommended AI Tools

| Tool | Best For | Free Tier |
|------|----------|-----------|
| ChatGPT | Detailed explanations | Yes (limited) |
| Gemini | Code analysis | Yes |
| Claude | Code quality | Yes (limited) |
| GitHub Copilot | Inline code suggestions | Paid |

## References
- ChatGPT: https://chat.openai.com
- Google Gemini: https://gemini.google.com
- uvloop docs: https://uvloop.readthedocs.io
- Async debugging: https://realpython.com/async-io-python/

## Key Takeaway

💡 **AI is a tool, not a replacement for understanding**

Use AI to:
- Speed up learning
- Explain concepts
- Find bugs quickly
- Optimize code

But always:
- Verify the answer
- Understand the fix
- Learn from mistakes
- Document your learning
