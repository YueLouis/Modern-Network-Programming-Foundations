"""
Benchmark script to compare threaded vs async servers
Usage: python benchmark_server.py <target_host:port> <num_connections> <requests_per_conn>
"""
import socket
import time
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

def send_request(host, port, num_requests):
    """Send multiple echo requests through single connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        start_time = time.time()
        for i in range(num_requests):
            message = f"Test message {i}".encode('utf-8')
            sock.send(message)
            response = sock.recv(1024)
        end_time = time.time()
        
        sock.close()
        return end_time - start_time
    except Exception as e:
        print(f"Error: {str(e)}")
        return -1

def benchmark(host, port, num_connections, requests_per_conn):
    """Run benchmark test"""
    print(f"\n{'='*60}")
    print(f"Benchmark Configuration:")
    print(f"  Target: {host}:{port}")
    print(f"  Concurrent Connections: {num_connections}")
    print(f"  Requests per Connection: {requests_per_conn}")
    print(f"  Total Requests: {num_connections * requests_per_conn}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Use thread pool for concurrent connections
    with ThreadPoolExecutor(max_workers=min(num_connections, 50)) as executor:
        futures = [
            executor.submit(send_request, host, port, requests_per_conn)
            for _ in range(num_connections)
        ]
        
        times = []
        for i, future in enumerate(futures):
            elapsed = future.result()
            if elapsed > 0:
                times.append(elapsed)
            print(f"  Connection {i+1}/{num_connections}: {elapsed:.3f}s")
    
    total_time = time.time() - start_time
    total_requests = num_connections * requests_per_conn
    
    print(f"\n{'='*60}")
    print(f"RESULTS:")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Requests/Second: {total_requests/total_time:.2f}")
    print(f"  Avg Latency: {sum(times)/len(times)*1000:.2f}ms")
    print(f"  Min Latency: {min(times)*1000:.2f}ms")
    print(f"  Max Latency: {max(times)*1000:.2f}ms")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python benchmark_server.py <host:port> <connections> <requests_per_conn>")
        print("Example: python benchmark_server.py localhost:9999 100 10")
        sys.exit(1)
    
    target = sys.argv[1].split(':')
    host = target[0]
    port = int(target[1])
    num_connections = int(sys.argv[2])
    requests_per_conn = int(sys.argv[3])
    
    benchmark(host, port, num_connections, requests_per_conn)
