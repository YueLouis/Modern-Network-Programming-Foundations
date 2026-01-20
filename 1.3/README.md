# Lab 1.3: Multi-threaded TCP Server

## Objective
Handle multiple TCP clients concurrently using threading

## Requirements

### Core Features
- ✅ Server listens on **port 9998**
- ✅ Each client handled in a separate **thread**
- ✅ Support concurrent connections
- ✅ Thread-safe data structures

### In-class Tasks
- ✅ Import `threading`
- ✅ `handle_client(client_socket)` function
- ✅ Spawn thread per `accept()`
- ✅ Test with multiple telnet connections

### Homework Tasks
- ✅ Limit max threads (e.g., 10)
- ✅ Implement thread pool / cap connections
- ✅ Track active connections count

## Implementation

### File Structure
```
1.3/
├── tcp_threaded_server.py  # Multi-threaded TCP echo server
└── README.md               # This file
```

### Features Implemented
- **Port 9998** TCP echo server
- **Thread per client**: each connection handled in its own thread
- **Connection limit**: max 10 concurrent connections; reject 11th+
- **Active connection tracking** with lock
- **Echo prefix**: `ECHO: <message>`
- **Graceful handling** of disconnects and errors

## How to Run
```bash
# Using Python
python 1.3/tcp_threaded_server.py

# Or using uv
uv run 1.3/tcp_threaded_server.py
```

Expected startup log:
```
Multi-threaded TCP Server listening on localhost:9998
Max threads: 10
```

## How to Test (PowerShell telnet / TCPClient)
Open nhiều terminal và chạy telnet:
```powershell
telnet localhost 9998
```
Hoặc dùng PowerShell TCPClient (nhiều phiên song song):
```powershell
$client = New-Object System.Net.Sockets.TcpClient("localhost", 9998)
$stream = $client.GetStream()
$w = New-Object System.IO.StreamWriter($stream)
$w.AutoFlush = $true
$r = New-Object System.IO.StreamReader($stream)
$w.WriteLine("Hello from client")
$r.ReadLine()
```

## Mass Test Script (PowerShell)
Tạo 7 client nhanh (ID 5..11) và gửi echo:
```powershell
$clients = 5..11 | ForEach-Object {
    $c = New-Object System.Net.Sockets.TcpClient("localhost", 9998)
    $s = $c.GetStream()
    $w = New-Object System.IO.StreamWriter($s); $w.AutoFlush = $true
    $r = New-Object System.IO.StreamReader($s)
    @{ Id=$_; Client=$c; Stream=$s; Writer=$w; Reader=$r }
}
foreach ($c in $clients) {
    $msg = "Client $($c.Id): Hello"
    $c.Writer.WriteLine($msg)
    $resp = $c.Reader.ReadLine()
    Write-Host "[$($c.Id)] -> $msg | <- $resp"
}
foreach ($c in $clients) { $c.Writer.Close(); $c.Stream.Close(); $c.Client.Close() }
```

## Sample Logs
```
Multi-threaded TCP Server listening on localhost:9998
Max threads: 10
Client connected: 127.0.0.1:1926 (Active: 1)
...
Client connected: 127.0.0.1:27361 (Active: 10)
WARNING - Max connections (10) reached. Rejecting connection from 127.0.0.1
```

## Technical Details
- **Concurrency model**: Thread-per-connection
- **Limit**: `max_threads=10`; 11th+ connection receives "Server is full"
- **Synchronization**: `Lock` guards active connection counter
- **Echo logic**: `recv(1024)` → `send(f"ECHO: {message}")`

### Thread Flow
```
Main thread:
  socket() → bind() → listen()
  loop accept():
    if active_connections >= max_threads:
        reject
    else:
        spawn Thread(handle_client)

handle_client thread:
  loop recv():
    if data empty: break
    send echo
  close socket
  decrement active counter
```

## Evaluation Criteria
| Criteria | Points | Status |
|----------|--------|--------|
| Multi-client support | 60% | ✅ Pass |
| Thread implementation | 30% | ✅ Pass |
| Resource management | 10% | ✅ Pass |
| **Total** | **100%** | **✅ Complete** |

## Known Limitations
- **Thread-per-connection** scales kém cho hàng nghìn clients (overhead lớn)
- Không có timeout; client giữ kết nối lâu sẽ chiếm slot
- Echo-only; không có broadcast hay shared state

## Next Steps
- **Lab 1.4:** Async TCP Server (async/await, scale tốt hơn)
- **Lab 1.5:** Packet crafting với Scapy

## References
- [Python socket](https://docs.python.org/3/library/socket.html)
- [threading](https://docs.python.org/3/library/threading.html)
- [Socket HOWTO](https://docs.python.org/3/howto/sockets.html)

---
**Status:** ✅ Complete  
**Time:** 60 phút  
**Difficulty:** ⭐⭐⭐⭐☆ (Intermediate)
