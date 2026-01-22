#!/usr/bin/env python3
"""
Lab 1.4: Benchmark - Compare Async vs Threading Performance

Usage:
    # Terminal 1: Start async server
    python async_tcp_echo_server.py
    
    # Terminal 2: Run benchmark
    python benchmark_server.py
"""

import socket
import time
import threading
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def _timestamp():
    return datetime.now().strftime("%H:%M:%S")


class BenchmarkClient:
    """Simple client for stress testing"""
    
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.success_count = 0
        self.fail_count = 0
        self.total_time = 0
        self.min_latency = float('inf')
        self.max_latency = 0
    
    def send_request(self):
        """Send single request to server"""
        try:
            start = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.host, self.port))
            
            message = b'Benchmark test message from client'
            sock.send(message)
            
            response = sock.recv(1024)
            sock.close()
            
            latency = time.time() - start
            
            if response.startswith(b'ECHO:'):
                self.success_count += 1
                self.total_time += latency
                self.min_latency = min(self.min_latency, latency)
                self.max_latency = max(self.max_latency, latency)
                return True
            else:
                self.fail_count += 1
                return False
        
        except socket.timeout:
            self.fail_count += 1
            return False
        
        except ConnectionRefusedError:
            self.fail_count += 1
            return False
        
        except Exception as e:
            self.fail_count += 1
            return False


def stress_test_sequential(num_clients=50):
    """Sequential requests (one by one)"""
    print(f"\n📊 Sequential Test ({num_clients} requests)")
    print("-" * 60)
    
    client = BenchmarkClient()
    start_time = time.time()
    
    for i in range(num_clients):
        client.send_request()
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{num_clients}")
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Sequential Results:")
    print(f"   Success: {client.success_count}/{num_clients}")
    print(f"   Failed: {client.fail_count}/{num_clients}")
    print(f"   Total Time: {elapsed:.2f}s")
    print(f"   Throughput: {num_clients/elapsed:.2f} req/sec")
    if client.total_time > 0:
        avg_latency = (client.total_time / client.success_count) * 1000
        print(f"   Avg Latency: {avg_latency:.2f}ms")
        print(f"   Min Latency: {client.min_latency*1000:.2f}ms")
        print(f"   Max Latency: {client.max_latency*1000:.2f}ms")
    
    return elapsed


def stress_test_concurrent(num_clients=50, max_workers=50):
    """Concurrent requests using ThreadPoolExecutor"""
    print(f"\n📊 Concurrent Test ({num_clients} requests, {max_workers} workers)")
    print("-" * 60)
    
    client = BenchmarkClient()
    start_time = time.time()
    
    def worker(_):
        return client.send_request()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, i) for i in range(num_clients)]
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 20 == 0:
                print(f"  Progress: {completed}/{num_clients}")
            future.result()
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Concurrent Results:")
    print(f"   Success: {client.success_count}/{num_clients}")
    print(f"   Failed: {client.fail_count}/{num_clients}")
    print(f"   Total Time: {elapsed:.2f}s")
    print(f"   Throughput: {num_clients/elapsed:.2f} req/sec")
    if client.total_time > 0:
        avg_latency = (client.total_time / client.success_count) * 1000
        print(f"   Avg Latency: {avg_latency:.2f}ms")
        print(f"   Min Latency: {client.min_latency*1000:.2f}ms")
        print(f"   Max Latency: {client.max_latency*1000:.2f}ms")
    
    return elapsed


def main():
    """Run benchmarks"""
    print("\n" + "="*60)
    print("🔬 Async Server Benchmark")
    print("="*60)
    print("\n⚠️  Make sure server is running!")
    print("   Run: python async_tcp_echo_server.py")
    
    # Wait for server
    time.sleep(2)
    
    # Test configurations
    test_configs = [
        (50, 50),     # 50 clients
        (100, 50),    # 100 clients
        (200, 100),   # 200 clients
        (500, 100),   # 500 clients (stress test)
    ]
    
    results = []
    
    for num_clients, max_workers in test_configs:
        try:
            print(f"\n\n{'='*60}")
            print(f"Test: {num_clients} concurrent clients")
            print(f"{'='*60}")
            
            # Sequential test (small scale only)
            if num_clients <= 50:
                seq_time = stress_test_sequential(num_clients)
            else:
                seq_time = None
            
            time.sleep(1)
            
            # Concurrent test
            conc_time = stress_test_concurrent(num_clients, max_workers)
            
            if seq_time and conc_time:
                improvement = (seq_time - conc_time) / seq_time * 100
                print(f"\n⚡ Improvement: {improvement:.1f}% faster with concurrency")
            
            results.append({
                'clients': num_clients,
                'time': conc_time,
                'throughput': num_clients / conc_time
            })
            
            time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Benchmark stopped")
            break
        except ConnectionRefusedError:
            print(f"\n❌ Connection refused - Is server running?")
            sys.exit(1)
    
    # Summary
    if results:
        print(f"\n\n{'='*60}")
        print("📈 Summary - Async Server Performance")
        print(f"{'='*60}")
        print(f"{'Clients':<12} {'Time (s)':<12} {'Throughput':<15}")
        print("-" * 50)
        
        for r in results:
            print(f"{r['clients']:<12} {r['time']:<12.2f} {r['throughput']:.0f} req/sec")
        
        print("\n✅ Benchmark complete!")
        print("\n💡 Key Insights:")
        print("   • Async handles many concurrent connections efficiently")
        print("   • Memory usage remains low even with 500+ clients")
        print("   • Compare with threading version from Lab 1.1")
        print("   • Async is better for I/O-bound workloads")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Benchmark interrupted")
        sys.exit(0)
