"""
Lab 1.5.3: HTTP Traffic Analyzer
Capture and analyze HTTP traffic to extract URLs
"""
import logging
from scapy.all import sniff, IP, TCP, Raw, conf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)
conf.verb = 0

class HTTPTrafficAnalyzer:
    def __init__(self, interface=None, packet_count=10):
        self.interface = interface
        self.packet_count = packet_count
        self.urls = set()
        self.http_requests = []
    
    def extract_urls_from_payload(self, payload):
        """Extract URLs from HTTP payload"""
        try:
            payload_str = payload.decode('utf-8', errors='ignore')
            
            # Look for GET/POST requests
            if 'GET' in payload_str or 'POST' in payload_str or 'Host:' in payload_str:
                lines = payload_str.split('\r\n')
                
                for line in lines:
                    if line.startswith('GET') or line.startswith('POST'):
                        parts = line.split()
                        if len(parts) >= 2:
                            url = parts[1]
                            self.urls.add(url)
                    elif line.startswith('Host:'):
                        host = line.split(':', 1)[1].strip()
                        return host
        except Exception as e:
            pass
        
        return None
    
    def packet_callback(self, packet):
        """Callback for each captured packet"""
        if packet.haslayer(IP) and packet.haslayer(TCP):
            ip_layer = packet[IP]
            tcp_layer = packet[TCP]
            
            # Check for HTTP traffic (port 80 or 8080)
            if tcp_layer.dport in [80, 8080] or tcp_layer.sport in [80, 8080]:
                
                # Check for payload
                if packet.haslayer(Raw):
                    payload = packet[Raw].load
                    host = self.extract_urls_from_payload(payload)
                    
                    if host:
                        logger.info(f"HTTP Request: {ip_layer.src}:{tcp_layer.sport} → "
                                   f"{ip_layer.dst}:{tcp_layer.dport}")
                        logger.info(f"  Host: {host}")
                        
                        self.http_requests.append({
                            'src_ip': ip_layer.src,
                            'src_port': tcp_layer.sport,
                            'dst_ip': ip_layer.dst,
                            'dst_port': tcp_layer.dport
                        })
    
    def analyze(self):
        """Start packet capture and analysis"""
        logger.info(f"\nCapturing {self.packet_count} packets on port 80 and 8080...")
        logger.info("(Make HTTP requests to see traffic)\n")
        logger.info("="*60)
        
        try:
            sniff(
                filter="tcp port 80 or tcp port 8080",
                prn=self.packet_callback,
                count=self.packet_count,
                timeout=120
            )
        except PermissionError:
            logger.error("Error: Requires administrator/root privileges to capture packets")
            return False
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
        
        logger.info("="*60)
        self.print_results()
        return True
    
    def print_results(self):
        """Print analysis results"""
        logger.info(f"\n--- Analysis Results ---")
        logger.info(f"Total HTTP Requests Captured: {len(self.http_requests)}")
        
        if self.urls:
            logger.info(f"Unique URLs/Paths Found: {len(self.urls)}")
            for url in sorted(self.urls):
                logger.info(f"  - {url}")
        else:
            logger.info("No URLs found in captured traffic")
        
        if self.http_requests:
            logger.info(f"\nHTTP Connections:")
            for req in self.http_requests:
                logger.info(f"  {req['src_ip']}:{req['src_port']} → "
                           f"{req['dst_ip']}:{req['dst_port']}")

def main():
    print("\n" + "="*60)
    print("Lab 1.5.3: HTTP Traffic Analyzer")
    print("="*60)
    print("\nNote: This requires administrator/root privileges")
    print("Make HTTP requests (e.g., curl http://example.com) in another terminal")
    
    try:
        count = int(input("\nNumber of packets to capture (default: 10): ") or "10")
    except ValueError:
        count = 10
    
    analyzer = HTTPTrafficAnalyzer(packet_count=count)
    analyzer.analyze()
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
