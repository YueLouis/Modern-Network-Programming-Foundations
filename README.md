# Network Programming Labs - Complete Guide

## Overview
This folder contains 6 labs covering network programming concepts:
- TCP/UDP socket programming
- Async/threaded servers
- Packet crafting and analysis
- Debugging and optimization

---

## Lab 1.1: TCP Echo Server ✓
**File:** `1.1/tcp_echo_server.py`

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
