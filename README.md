# 📡 NPRO: Modern Network Programming Foundations
**Lab 1.1-1.6: Complete Guide (Lý Thuyết + Thực Hành)**

## 🎯 Mục Tiêu Chung
Hiểu sâu network programming từ **blocking socket → async/await**, **packet crafting**, và **production-ready code**.

**Key progression:** 1 client → 1000+ clients (async) → debug & optimize

---

## 📚 LÝ THUYẾT TRỌNG TÂM

### Scaling Concurrency (Progression)

```
Lab 1.1: Blocking Socket
├─ 1 client/server
├─ recv() block → chờ client
└─ Limitation: không scale

Lab 1.2: UDP (Connectionless)
├─ Datagram-based
├─ recvfrom() → biết ai gửi
└─ Dùng: DNS, Gaming, VoIP

Lab 1.3: Threading (1 thread/client)
├─ Xử lý concurrent
├─ Memory: ~1MB/thread
├─ GIL overhead
└─ Max: ~100-1000 clients

Lab 1.4: Async/Await (Event Loop) ⭐
├─ 1 thread, 1000+ clients
├─ Memory: ~50KB/coroutine
├─ Throughput: 600-900 req/s
├─ 160x more efficient
└─ Key: await = pause, let others run

Lab 1.5: Packet Crafting (Deep Dive)
├─ OSI layers (IP/TCP/ICMP)
├─ TCP 3-way handshake
├─ TCP SYN scanning
└─ Packet sniffing (Scapy)

Lab 1.6: Debug & Optimize
├─ 8 common bugs
├─ AI-assisted debugging
├─ Scale to 10,000+ connections
└─ Graceful shutdown
```

### TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| **Connection** | 3-way handshake | Connectionless |
| **Reliability** | Guaranteed | Best effort |
| **Order** | Ordered | May reorder |
| **Speed** | Slower (overhead) | Faster |
| **Header size** | 20 bytes | 8 bytes |
| **Use case** | HTTP, SSH, FTP | DNS, Gaming, VoIP |

### Threading vs Async

```python
# THREADING: 1 thread = 1 client
for client in clients:
    thread = threading.Thread(target=handle, args=(client,))
    thread.start()  # Spawn new thread
# Result: 100 threads = 100MB RAM, context switching overhead

# ASYNC: 1 thread = 1000+ clients
async def handle(reader, writer):
    while True:
        data = await reader.read()  # Pause, let others run
        ...
asyncio.run(main())
# Result: 1000 coroutines = ~50MB RAM, no context switch
```

### TCP 3-way Handshake

```
Client                    Server
  │                         │
  ├─── SYN (seq=x) ───────→ │
  │    (flags="S")          │
  │                         │
  │ ← SYN-ACK (ack=x+1) ─── │
  │   (flags="SA", seq=y)   │
  │                         │
  ├─── ACK (ack=y+1) ──────→│
  │    (flags="A")          │
  │                         │
  └─── Connected ──────────→│
       (data can flow)
```

### OSI Model (Layers)

```
7: Application    ← HTTP, DNS, SSH
6: Presentation   ← Encryption, compression
5: Session        ← Connection mgmt
4: Transport      ← TCP, UDP (reliability)
3: Network        ← IP (routing)
2: Data Link      ← MAC/Ethernet
1: Physical       ← Cables
```

---

## 💻 THỰC HÀNH (Labs)
**File:** `1.1/tcp_echo_server.py`

---

## 🏆 EXAM FOCUS POINTS

### "Nêu khác biệt TCP vs UDP?"
**Answer:** TCP = connection-based (handshake), reliable (ordered), overhead cao | UDP = connectionless, best-effort, datagram, nhanh

### "Tại sao async tốt hơn threading?"
**Answer:** Threading 1 thread=1 client (~1MB), GIL overhead | Async 1 thread=1000+ clients (~50KB), **160x efficient**

### "Memory leak async?"
**Answer:** Quên `writer.close()` → file descriptor leak | Không remove client → memory grows

### "TCP SYN scan?"
**Answer:** Gửi SYN → SYN-ACK=OPEN | RST-ACK=CLOSED | Timeout=FILTERED

### "Scale to 10k connections?"
**Answer:** OS tuning (ulimit), backpressure, multiple processes (reuse_port), uvloop, proper timeout + shutdown

---

## 📝 CODE TEMPLATES

**Async Handler:**
```python
async def handle(reader, writer):
    try:
        while True:
            data = await asyncio.wait_for(reader.read(1024), timeout=60)
            if not data: break
            try:
                msg = data.decode('utf-8', errors='replace')
            except: continue
            writer.write(f"ECHO: {msg}".encode())
            await writer.drain()
    finally:
        writer.close(); await writer.wait_closed()
```

**TCP Port Scanner:**
```python
from scapy.all import IP, TCP, sr1
syn = IP(dst=target)/TCP(dport=port, flags="S")
resp = sr1(syn, timeout=1)
if resp and resp[TCP].flags=="SA": print("OPEN")
```

---

## 📊 PERFORMANCE & STATUS

| Lab | File | Status | Metric |
|-----|------|--------|--------|
| 1.4 | async_tcp_echo_server.py | ✅ | 600-900 req/s, 50KB/conn |
| 1.5 | port_scanner.py | ✅ | Detected port 9999 |
| 1.5 | http_traffic_analyzer.py | ✅ | Captured neverssl.com |
| 1.6 | optimized_server.py | ✅ | 8 bugs fixed |

---

## ✅ FINAL NOTES

**Progression:** Blocking (1 client) → Threading (100 clients) → **Async (10k clients, 160x efficient)** → Packet Analysis → Production

---

**Features:**
- TCP server on port 9999
- Echo messages back with "ECHO: " prefix
- Logging with timestamps and client IP
- Special command: "TIME" returns server time
- Graceful disconnect handling

**Run:**
```bash
python 1.1/tcp_echo_server.py
```

**Test:**
```bash
telnet localhost 9999
# Type: Hello
# Get: ECHO: HELLO
# Type: TIME
# Get: SERVER TIME: 2025-01-20 14:30:45
```

---

## Lab 1.2: UDP Chat Application ✓
**Files:** 
- `1.2/udp_chat_server.py` - Broadcast server
- `1.2/udp_chat_client.py` - Chat client

**Features:**
- UDP broadcast messaging
- Nickname system
- Connection notifications
- Multi-client support

**Run:**
```bash
# Terminal 1 - Server
python 1.2/udp_chat_server.py

# Terminal 2 - Client 1
python 1.2/udp_chat_client.py
# Enter nickname: Alice

# Terminal 3 - Client 2
python 1.2/udp_chat_client.py
# Enter nickname: Bob
```

---

## Lab 1.3: Multi-threaded TCP Server ✓
**File:** `1.3/tcp_threaded_server.py`

**Features:**
- Multi-client TCP server on port 9998
- Each client in separate thread
- Max 10 concurrent connections
- Active connection tracking
- Resource management

**Run:**
```bash
python 1.3/tcp_threaded_server.py
```

**Test (multiple terminals):**
```bash
telnet localhost 9998
# Do this in 2-3 different terminals simultaneously
```

---

## Lab 1.4: Async Network Applications ✓
**File:** `1.4/async_tcp_echo_server.py`

**Features:**
- Async echo server on port 9999
- 30-second idle timeout
- Real-time metrics (requests, active connections)
- Graceful shutdown (Ctrl+C)
- Supports 100+ concurrent connections

**Benchmark Tool:** `1.4/benchmark_server.py`

**Run:**
```bash
# Terminal 1
python 1.4/async_tcp_echo_server.py

# Terminal 2 - Benchmark
python 1.4/benchmark_server.py localhost:9999 100 20
# 100 connections, 20 requests each
```

**Performance Comparison:**
```bash
# Compare with threaded server
python 1.3/tcp_threaded_server.py
python 1.4/benchmark_server.py localhost:9998 100 20

vs

python 1.4/async_tcp_echo_server.py
python 1.4/benchmark_server.py localhost:9999 100 20
```

---

## Lab 1.5: Packet Crafting with Scapy

⚠️ **Requires administrator/root privileges!**

### 1.5.1: Packet Crafting
**File:** `1.5/packet_crafting.py`

**Features:**
- ICMP ping (Ping.com DNS)
- TCP SYN scanning (port detection)
- Demonstrates packet structure

**Run:**
```bash
# Windows - Run as Administrator
python 1.5/packet_crafting.py

# Linux/Mac
sudo python 1.5/packet_crafting.py
```

### 1.5.2: Port Scanner
**File:** `1.5/port_scanner.py`

**Features:**
- Scan port range (default: 20-100)
- Detect open/closed ports
- Interactive interface

**Run:**
```bash
python 1.5/port_scanner.py
# Enter target: google.com
# Enter start port: 80
# Enter end port: 443
```

### 1.5.3: HTTP Traffic Analyzer
**File:** `1.5/http_traffic_analyzer.py`

**Features:**
- Capture HTTP traffic on port 80
- Extract URLs and hosts
- Packet analysis

**Run (Admin):**
```bash
# Terminal 1
python 1.5/http_traffic_analyzer.py

# Terminal 2 - Make HTTP requests
curl http://example.com
```

### 1.5.4: ARP Spoof Detector
**File:** `1.5/arp_spoof_detector.py`

**Features:**
- Monitor ARP traffic
- Detect duplicate IPs (spoofing)
- Track IP-to-MAC mapping

**Run (Admin):**
```bash
python 1.5/arp_spoof_detector.py
```

**Generate ARP traffic:**
```bash
# Windows
arp -a

# Linux
ping other-host
```

---

## Lab 1.6: AI-Enhanced Debugging

### 1.6.1: Buggy Server
**File:** `1.6/buggy_server.py`

**Intentional Bugs:**
1. Unbounded client list (memory leak)
2. No exception handling (crashes on bad data)
3. Unbounded request queue (memory grows)
4. No connection cleanup (resource leak)
5. No idle timeout (zombie connections)

**Behavior:**
- Crashes after ~5 connections
- Memory usage spikes
- Slow degradation

### 1.6.2: Fixed Server
**File:** `1.6/fixed_server.py`

**Improvements:**
- Proper client tracking and cleanup
- Bounded queues with maxlen
- Exception handling
- 30-second idle timeout
- Connection resource limits
- Real-time metrics

**Optional: UV Loop Integration**
```python
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# 2-4x performance improvement!
```

### 1.6.3: Debugging Guide
**File:** `1.6/debugging_guide.py`

**Contains:**
- AI prompts for ChatGPT/Gemini
- Bug identification checklist
- Optimization techniques
- Performance benchmarking guide

**Run:**
```bash
python 1.6/debugging_guide.py
```

---

## Quick Start - All Labs

```bash
# 1. TCP Echo Server
python 1.1/tcp_echo_server.py

# 2. UDP Chat (3 terminals)
python 1.2/udp_chat_server.py
python 1.2/udp_chat_client.py  # Terminal 2
python 1.2/udp_chat_client.py  # Terminal 3

# 3. Threaded Server
python 1.3/tcp_threaded_server.py

# 4. Async Server + Benchmark
python 1.4/async_tcp_echo_server.py
python 1.4/benchmark_server.py localhost:9999 50 20

# 5. Packet Tools (Admin)
python 1.5/packet_crafting.py
python 1.5/port_scanner.py
python 1.5/http_traffic_analyzer.py
python 1.5/arp_spoof_detector.py

# 6. Debugging Comparison
python 1.6/buggy_server.py     # Crashes
python 1.6/fixed_server.py     # Works well
python 1.6/debugging_guide.py  # Learn how to debug
```

---

## Installation & Setup

```bash
# Install dependencies
pip install scapy uvloop

# Verify Python version
python --version  # Should be 3.7+

# Test imports
python -c "import asyncio, scapy, uvloop; print('All dependencies OK')"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Port already in use" | Change port in code or wait 60s |
| "PermissionError" on Scapy | Run with admin/sudo |
| "ModuleNotFoundError: scapy" | `pip install scapy` |
| "Cannot connect" to server | Check firewall, ensure server running |
| "Slow performance" | Try uvloop: `pip install uvloop` |

---

## Learning Outcomes

After completing these labs, you will understand:

✓ TCP/UDP socket programming  
✓ Async vs threaded servers  
✓ Network packet structure  
✓ Protocol analysis  
✓ Performance optimization  
✓ Debugging techniques  
✓ Production-ready error handling  

---

## Additional Resources

- [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
- [Scapy documentation](https://scapy.readthedocs.io/)
- [uvloop GitHub](https://github.com/MagicStack/uvloop)

---

**Good luck with your networking labs!** 🚀
D:
