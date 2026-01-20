"""
Lab 1.5.2: Port Scanner
Scan a range of ports on target host
"""
import logging
import sys
from scapy.all import IP, TCP, sr1, conf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)
conf.verb = 0

class PortScanner:
    def __init__(self, target, start_port=20, end_port=100, timeout=1):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.open_ports = []
    
    def scan_port(self, port):
        """Scan single port"""
        try:
            syn = IP(dst=self.target) / TCP(dport=port, flags="S")
            response = sr1(syn, timeout=self.timeout)
            
            if response:
                if response.haslayer(TCP) and response[TCP].flags == "SA":
                    logger.info(f"✓ Port {port:5}/tcp OPEN")
                    self.open_ports.append(port)
                    return "open"
            return "closed"
        except Exception as e:
            logger.error(f"Error scanning port {port}: {str(e)}")
            return "error"
    
    def scan_range(self):
        """Scan port range"""
        logger.info(f"\nScanning {self.target} ports {self.start_port}-{self.end_port}...")
        logger.info("="*50)
        
        for port in range(self.start_port, self.end_port + 1):
            self.scan_port(port)
        
        logger.info("="*50)
        if self.open_ports:
            logger.info(f"\nOpen ports found: {self.open_ports}")
        else:
            logger.info("\nNo open ports found in range")
    
    def get_results(self):
        return self.open_ports

def main():
    print("\n" + "="*60)
    print("Lab 1.5.2: TCP Port Scanner")
    print("="*60)
    
    target = input("Enter target IP/hostname (default: localhost): ").strip()
    if not target:
        target = "localhost"
    
    try:
        start = int(input("Enter start port (default: 20): ") or "20")
        end = int(input("Enter end port (default: 100): ") or "100")
    except ValueError:
        start, end = 20, 100
    
    scanner = PortScanner(target, start, end)
    scanner.scan_range()
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
