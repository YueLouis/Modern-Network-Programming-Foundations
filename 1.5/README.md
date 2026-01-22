# Lab 1.5: Packet Crafting with Scapy (60 minutes)

## Objective
Create, craft, and analyze packets using Scapy library

## Why Scapy?
Scapy is a powerful Python library for:
- Creating custom network packets (layer 2-7)
- Sending and receiving packets
- Sniffing and analyzing traffic
- Building network security tools

## Requirements
```bash
# Install Scapy
pip install scapy

# Windows: Run as Administrator
# Linux/Mac: Use sudo
```

## Theory

### OSI Model Layers (What we'll craft)
```
Layer 7: Application (HTTP, DNS, SSH) ← Highest level
Layer 4: Transport (TCP, UDP)
Layer 3: Network (IP)
Layer 2: Data Link (Ethernet)
Layer 1: Physical
```

### Scapy Packet Structure
```python
packet = IP(dst="8.8.8.8") / ICMP()
         │                  │
         └─ Layer 3 (Network) Layer 4 (Transport)
         
# Full packet:
# Ethernet / IP / TCP / Raw(payload)
```

## In-Class Tasks

### Task 1: Craft ICMP Ping Packet

```python
from scapy.all import IP, ICMP, sr1

# Create ICMP ping packet
packet = IP(dst="8.8.8.8") / ICMP()

print("[*] Sending ping to 8.8.8.8...")
reply = sr1(packet, timeout=2)

if reply:
    print(f"[+] Reply from {reply.src}")
    print(f"    TTL: {reply.ttl}")
    print(f"    Sequence: {reply[ICMP].seq}")
else:
    print("[-] No reply (timeout or filtered)")
```

**What's happening:**
- `IP(dst="8.8.8.8")` - Create IP packet destined to Google DNS
- `ICMP()` - Add ICMP echo request (ping)
- `sr1()` - Send and receive 1 response
- `reply.src` - Source IP of the reply (usually same as dst)

### Task 2: Craft TCP SYN Packet (Port Scanner)

```python
from scapy.all import IP, TCP, sr1

# Check if port 80 is open
target = "192.168.1.1"
port = 80

syn_packet = IP(dst=target) / TCP(dport=port, flags="S")

print(f"[*] Scanning {target}:{port}...")
response = sr1(syn_packet, timeout=1)

if response:
    if response.haslayer(TCP):
        if response[TCP].flags == "SA":  # SYN-ACK
            print(f"[+] Port {port} is OPEN")
        elif response[TCP].flags == "RA":  # RST-ACK
            print(f"[-] Port {port} is CLOSED")
else:
    print(f"[?] Port {port} is FILTERED (no response)")
```

**TCP Handshake (3-way):**
```
Client                           Server
  │                               │
  ├─── SYN (flags="S") ─────────→ │
  │                               │
  │ ← SYN-ACK (flags="SA") ──────┤
  │                               │
  ├─── ACK (flags="A") ─────────→ │
  │                               │
  └─────── Connected! ────────────┘
```

### Task 3: Packet Analysis (Sniffing)

```python
from scapy.all import sniff, IP, TCP

def packet_callback(packet):
    """Analyze each captured packet"""
    if packet.haslayer(TCP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        tcp_sport = packet[TCP].sport
        tcp_dport = packet[TCP].dport
        
        print(f"{ip_src}:{tcp_sport} → {ip_dst}:{tcp_dport}")

print("[*] Sniffing TCP traffic on port 80...")
sniff(
    filter="tcp port 80",
    prn=packet_callback,
    count=10  # Capture 10 packets
)
```

**Filter syntax:**
- `tcp port 80` - TCP traffic on port 80
- `udp port 53` - DNS queries
- `icmp` - ICMP packets
- `tcp.flags.syn==1` - TCP SYN packets only

## Homework Tasks

### Task 1: Port Scanner (ports 20-100)

Create: `port_scanner.py`

```python
from scapy.all import IP, TCP, sr, conf
import sys

def scan_ports(target, start_port=20, end_port=100):
    """Scan ports on target host"""
    
    # Suppress Scapy warnings
    conf.verb = 0
    
    print(f"[*] Scanning {target} (ports {start_port}-{end_port})...\n")
    
    open_ports = []
    
    for port in range(start_port, end_port + 1):
        syn = IP(dst=target) / TCP(dport=port, flags="S")
        resp = sr1(syn, timeout=0.5)
        
        if resp:
            if resp[TCP].flags == "SA":  # SYN-ACK
                open_ports.append(port)
                print(f"[+] Port {port}: OPEN")
            elif resp[TCP].flags == "RA":  # RST-ACK
                print(f"[-] Port {port}: CLOSED")
        else:
            print(f"[?] Port {port}: FILTERED")
    
    print(f"\n[+] Open ports: {open_ports}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python port_scanner.py <target_ip>")
        sys.exit(1)
    
    target = sys.argv[1]
    scan_ports(target)
```

**Usage:**
```bash
# Scan your router or localhost
python port_scanner.py 192.168.1.1
python port_scanner.py 127.0.0.1
```

### Task 2: HTTP Traffic Analysis

Create: `http_traffic_analyzer.py`

```python
from scapy.all import sniff, IP, TCP, Raw
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_http(packet):
    """Extract HTTP information from packets"""
    
    if packet.haslayer(IP) and packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        
        # Monitor ports 80 and 8080
        if tcp_layer.dport in [80, 8080] or tcp_layer.sport in [80, 8080]:
            # Check if payload exists (HTTP data)
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                
                try:
                    http_data = payload.decode('utf-8', errors='ignore')
                    
                    # Look for HTTP GET/POST
                    if 'GET' in http_data or 'POST' in http_data or 'Host:' in http_data:
                        logger.info(f"HTTP Request: {packet[IP].src}:{tcp_layer.sport} → {packet[IP].dst}:{tcp_layer.dport}")
                        
                        # Extract host header
                        for line in http_data.split('\r\n'):
                            if line.startswith('Host:'):
                                logger.info(f"  Host: {line.split(':', 1)[1].strip()}")
                except:
                    pass

if __name__ == "__main__":
    print("[*] Sniffing HTTP traffic on ports 80 and 8080...")
    print("[!] Make HTTP requests (not HTTPS) in another terminal\n")
    
    sniff(
        filter="tcp port 80 or tcp port 8080",
        prn=analyze_http,
        timeout=120  # Wait 2 minutes
    )
```

### Task 3: ARP Spoof Detector

Create: `arp_spoof_detector.py`

```python
from scapy.all import sniff, ARP
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARPSpoofDetector:
    def __init__(self):
        self.ip_mac_map = defaultdict(set)
        self.suspicious_ips = defaultdict(int)
    
    def packet_callback(self, packet):
        """Process ARP packets"""
        if packet.haslayer(ARP):
            arp_layer = packet[ARP]
            
            if arp_layer.op == 2:  # ARP reply
                src_ip = arp_layer.psrc
                src_mac = arp_layer.hwsrc
                
                logger.info(f"ARP Reply: {src_ip} is at {src_mac}")
                
                # Check for duplicate IPs (spoof)
                if src_ip in self.ip_mac_map:
                    if src_mac not in self.ip_mac_map[src_ip]:
                        logger.warning(f"⚠️  ALERT: Duplicate IP detected!")
                        logger.warning(f"   IP {src_ip} now: {src_mac}")
                        self.suspicious_ips[src_ip] += 1
                
                self.ip_mac_map[src_ip].add(src_mac)

if __name__ == "__main__":
    detector = ARPSpoofDetector()
    
    print("[*] Monitoring ARP traffic for spoofing...")
    print("[!] Generate ARP traffic: ping hosts on your network\n")
    
    sniff(
        filter="arp",
        prn=detector.packet_callback,
        timeout=120  # 2 minutes
    )
    
    # Results
    print(f"\n[+] Total IPs seen: {len(detector.ip_mac_map)}")
    if detector.suspicious_ips:
        print("⚠️  Suspicious IPs:")
        for ip, count in detector.suspicious_ips.items():
            print(f"   {ip}: {count} conflicts")
    else:
        print("[✓] No spoofing detected")
```

## Scapy Common Functions

### Sending Packets
| Function | Purpose |
|----------|---------|
| `send(pkt)` | Send packet (no response) |
| `sr(pkt)` | Send and receive all responses |
| `sr1(pkt)` | Send and receive 1 response |
| `sniff()` | Capture packets from network |

### Packet Layers
| Layer | Scapy Module |
|-------|-------------|
| Ethernet | `Ether` |
| IP | `IP` |
| TCP | `TCP` |
| UDP | `UDP` |
| ICMP | `ICMP` |
| DNS | `DNS` |
| Raw Data | `Raw` |

### Checking Layers
```python
if packet.haslayer(TCP):
    tcp_data = packet[TCP]
    print(tcp_data.sport, tcp_data.dport)
```

## Evaluation Rubric
- **Packet crafting**: 50%
  - ✅ Create ICMP packets
  - ✅ Create TCP SYN packets
  - ✅ Proper layer composition

- **Analysis logic**: 40%
  - ✅ Correctly identify packets
  - ✅ Extract relevant information
  - ✅ Filter and process traffic

- **Code organization**: 10%
  - ✅ Clean, readable code
  - ✅ Error handling
  - ✅ Comments

## Common Issues

### ⚠️ Permission Denied
```
Error: [Errno 1] Operation not permitted
```
**Solution:** Run with administrator/root privileges
- Windows: `Run as Administrator`
- Linux: `sudo python script.py`

### ⚠️ No Responses on Ping
Firewall may block ICMP. Test with localhost or known-open ports.

### ⚠️ Scapy Not Found
```bash
pip install scapy
```

## Security & Ethics

⚠️ **Important**: Only use these tools on:
- Your own computers
- Networks you have permission to test
- Educational environments

Port scanning without permission is **illegal** in many jurisdictions.

## References
- Scapy docs: https://scapy.readthedocs.io/
- IP/ICMP: https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol
- TCP/IP: https://en.wikipedia.org/wiki/Transmission_Control_Protocol
