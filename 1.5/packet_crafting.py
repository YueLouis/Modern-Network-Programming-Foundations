"""
Lab 1.5.1: Packet Crafting - ICMP Ping and TCP SYN
Requirements: pip install scapy
"""
import logging
from scapy.all import IP, ICMP, TCP, sr1, conf

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Suppress verbose output
conf.verb = 0

def ping_target(target_ip):
    """Send ICMP ping to target"""
    logger.info(f"\n[ICMP PING] Sending ping to {target_ip}...")
    
    try:
        packet = IP(dst=target_ip) / ICMP()
        reply = sr1(packet, timeout=3)
        
        if reply:
            logger.info(f"✓ Reply from {reply.src}: ttl={reply.ttl}")
            return True
        else:
            logger.warning(f"✗ No response from {target_ip}")
            return False
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def scan_tcp_port(target_ip, target_port):
    """Send TCP SYN to check if port is open"""
    logger.info(f"\n[TCP SYN] Scanning {target_ip}:{target_port}...")
    
    try:
        syn = IP(dst=target_ip) / TCP(dport=target_port, flags="S")
        response = sr1(syn, timeout=3)
        
        if response:
            if response.haslayer(TCP):
                tcp_layer = response[TCP]
                
                if tcp_layer.flags == "SA":  # SYN-ACK received
                    logger.info(f"✓ Port {target_port}/tcp OPEN")
                    return "open"
                elif tcp_layer.flags == "RA":  # RST-ACK received
                    logger.warning(f"✗ Port {target_port}/tcp CLOSED")
                    return "closed"
            else:
                logger.warning(f"? Unexpected response from {target_ip}")
                return "unknown"
        else:
            logger.warning(f"✗ No response from {target_ip}:{target_port} (filtered)")
            return "filtered"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return "error"

def main():
    print("\n" + "="*60)
    print("Lab 1.5.1: Packet Crafting with Scapy")
    print("="*60)
    
    # Test ICMP ping
    print("\n--- ICMP Ping Test ---")
    ping_target("8.8.8.8")  # Google DNS
    ping_target("1.1.1.1")  # Cloudflare DNS
    
    # Test TCP SYN (requires elevated privileges on some systems)
    print("\n--- TCP SYN Scan Test ---")
    # Note: These examples use common public services
    scan_tcp_port("google.com", 80)
    scan_tcp_port("google.com", 443)
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
