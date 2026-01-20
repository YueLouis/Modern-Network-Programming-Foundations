# Lab 1.1: TCP Echo Server

## Objective
Build TCP server that receives data and echoes it back to client

## Requirements

### Core Features
- ✅ Server listens on **port 9999**
- ✅ Receive message from client
- ✅ Echo back with prefix **"ECHO: "**
- ✅ Handle multiple clients (sequential, one at a time)

### In-class Tasks
- ✅ Create basic server with socket, bind, listen, accept
- ✅ Implement recv/send logic
- ✅ Test with telnet: `telnet localhost 9999`

### Homework Tasks
- ✅ Add logging (timestamp, client IP)
- ✅ Handle client disconnect gracefully
- ✅ Add command: **"TIME"** → return server time

## Implementation

### File Structure
```
1.1/
├── tcp_echo_server.py    # Main server implementation
└── README.md            # This file
```

### Features Implemented

#### 1. Logging System
- Timestamps for all events
- Client IP and port tracking
- Connection/disconnection notifications

#### 2. Echo Functionality
- Receives messages from client
- Responds with "ECHO: " prefix
- Handles UTF-8 encoding

#### 3. Special Commands
- **TIME**: Returns current server time in format `YYYY-MM-DD HH:MM:SS`

#### 4. Error Handling
- Graceful disconnect handling
- Exception catching
- Proper resource cleanup

## How to Run

### Start Server
```bash
# Using Python directly
python tcp_echo_server.py

# Or using uv
uv run tcp_echo_server.py
```

### Expected Output
```
2026-01-20 09:06:10,413 - INFO - TCP Echo Server listening on port 9999...
```

## How to Test

### Method 1: Using Telnet
```bash
telnet localhost 9999
```

Then type messages:
```
Hello World
> ECHO: Hello World

TIME
> SERVER TIME: 2026-01-20 14:30:45
```

### Method 2: Using PowerShell
```powershell
$client = New-Object System.Net.Sockets.TcpClient("localhost", 9999)
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream) { AutoFlush = $true }
$reader = New-Object System.IO.StreamReader($stream)

# Test echo
$writer.WriteLine("Hello Server")
$response = $reader.ReadLine()
Write-Host "Response: $response"

# Test TIME command
$writer.WriteLine("TIME")
$response = $reader.ReadLine()
Write-Host "Time: $response"

$client.Close()
```

### Method 3: Using Python Client
```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9999))

# Send message
client.send(b"Hello from Python\n")
response = client.recv(1024).decode('utf-8')
print(f"Response: {response}")

# Test TIME command
client.send(b"TIME\n")
response = client.recv(1024).decode('utf-8')
print(f"Time: {response}")

client.close()
```

## Server Logs Example

```
2026-01-20 09:06:10,413 - INFO - TCP Echo Server listening on port 9999...
2026-01-20 09:10:55,236 - INFO - Client connected from 127.0.0.1:10963
2026-01-20 09:10:55,241 - INFO - Received from 127.0.0.1: Hello World
2026-01-20 09:10:55,241 - INFO - Sent to 127.0.0.1: ECHO: Hello World
2026-01-20 09:11:02,156 - INFO - Received from 127.0.0.1: TIME
2026-01-20 09:11:02,157 - INFO - Sent to 127.0.0.1: SERVER TIME: 2026-01-20 09:11:02
2026-01-20 09:11:15,432 - INFO - Client 127.0.0.1:10963 disconnected
2026-01-20 09:11:15,433 - INFO - Connection closed with 127.0.0.1:10963
```

## Technical Details

### Protocol
- **Transport:** TCP (SOCK_STREAM)
- **Port:** 9999
- **Host:** localhost (127.0.0.1)
- **Encoding:** UTF-8

### Connection Flow
```
1. Server: socket() → bind() → listen()
2. Server: accept() [WAITING]
3. Client: connect()
4. Server: recv() → process → send()
5. Server: loop back to recv()
6. Client: close() or disconnect
7. Server: cleanup → accept() [WAITING for next client]
```

### Concurrency Model
- **Sequential/Blocking:** One client at a time
- When a client is connected, server serves only that client
- Next client must wait until current client disconnects

## Evaluation Criteria

| Criteria | Points | Status |
|----------|--------|--------|
| Server runs | 60% | ✅ Pass |
| Echo works correctly | 30% | ✅ Pass |
| Error handling | 10% | ✅ Pass |
| **Total** | **100%** | **✅ Complete** |

## Known Limitations

1. **Sequential only**: Cannot handle multiple clients simultaneously
   - Solution: See Lab 1.3 (Multi-threaded) or Lab 1.4 (Async)

2. **No timeout**: Client can hold connection indefinitely
   - Solution: Add `socket.settimeout()` or use async with timeout

3. **Buffer size**: Fixed 1024 bytes
   - Large messages may need multiple recv() calls

## Next Steps

- **Lab 1.2:** UDP Chat Application (broadcast messages)
- **Lab 1.3:** Multi-threaded TCP Server (concurrent clients)
- **Lab 1.4:** Async TCP Server (thousands of connections)

## References

- [Python socket documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)

---

**Status:** ✅ Complete  
**Time Required:** 45 minutes  
**Difficulty:** ⭐⭐☆☆☆ (Beginner)
