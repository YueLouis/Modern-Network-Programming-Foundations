"""
Lab 1.5.4: ARP Spoof Detector
Detect duplicate IPs and ARP spoofing attacks
"""
import logging
from scapy.all import ARP, sniff, conf
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)
conf.verb = 0

class ARPSpoofDetector:
    def __init__(self, packet_count=100):
        self.packet_count = packet_count
        # Map IP to MAC addresses seen
        self.ip_mac_map = defaultdict(set)
        # Track potential spoofing
        self.suspicious_ips = defaultdict(int)
    
    def packet_callback(self, packet):
        """Process ARP packets"""
        if packet.haslayer(ARP):
            arp_layer = packet[ARP]
            
            # Only monitor replies and requests
            if arp_layer.op == 2:  # ARP reply (op=2)
                src_ip = arp_layer.psrc
                src_mac = arp_layer.hwsrc
                
                logger.info(f"ARP Reply: {src_ip} is at {src_mac}")
                
                # Check for duplicate IPs (potential spoof)
                if src_ip in self.ip_mac_map:
                    if src_mac not in self.ip_mac_map[src_ip]:
                        logger.warning(f"⚠️  ALERT: Duplicate IP detected!")
                        logger.warning(f"   IP {src_ip} previously: {self.ip_mac_map[src_ip]}")
                        logger.warning(f"   IP {src_ip} now claims: {src_mac}")
                        self.suspicious_ips[src_ip] += 1
                
                self.ip_mac_map[src_ip].add(src_mac)
    
    def analyze(self):
        """Start ARP monitoring"""
        logger.info(f"\nMonitoring ARP traffic for {self.packet_count} packets...")
        logger.info("(Generate ARP traffic with ping or arp -a)\n")
        logger.info("="*60)
        
        try:
            sniff(
                filter="arp",
                prn=self.packet_callback,
                count=self.packet_count,
                timeout=60
            )
        except PermissionError:
            logger.error("Error: Requires administrator/root privileges")
            return False
        except KeyboardInterrupt:
            logger.info("Stopping capture...")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
        
        logger.info("="*60)
        self.print_results()
        return True
    
    def print_results(self):
        """Print analysis results"""
        logger.info(f"\n--- ARP Analysis Results ---")
        logger.info(f"Total unique IPs seen: {len(self.ip_mac_map)}")
        
        logger.info(f"\nIP to MAC mapping:")
        for ip in sorted(self.ip_mac_map.keys()):
            macs = self.ip_mac_map[ip]
            if len(macs) > 1:
                logger.warning(f"  ⚠️  {ip}: {macs}")
            else:
                logger.info(f"  ✓ {ip}: {list(macs)[0]}")
        
        if self.suspicious_ips:
            logger.warning(f"\n⚠️  SUSPICIOUS IPs (possible spoofing):")
            for ip, count in sorted(self.suspicious_ips.items(), 
                                   key=lambda x: x[1], reverse=True):
                logger.warning(f"   {ip}: {count} conflicts detected")
        else:
            logger.info(f"\n✓ No ARP spoofing detected")

def main():
    print("\n" + "="*60)
    print("Lab 1.5.4: ARP Spoof Detector")
    print("="*60)
    print("\nNote: Requires administrator/root privileges")
    print("To generate ARP traffic:")
    print("  Windows: arp -a")
    print("  Linux/Mac: arp-scan -l or ping other hosts")
    
    try:
        count = int(input("\nPackets to monitor (default: 100): ") or "100")
    except ValueError:
        count = 100
    
    detector = ARPSpoofDetector(packet_count=count)
    detector.analyze()
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
