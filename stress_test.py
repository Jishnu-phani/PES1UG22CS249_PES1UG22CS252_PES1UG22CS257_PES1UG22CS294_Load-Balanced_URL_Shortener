#!/usr/bin/env python3
import requests
import time
import random
import string
import threading
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

def generate_random_url():
    """Generate a random URL-like string"""
    domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    path = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
    return f"https://{domain}.com/{path}"

def shorten_url(base_url, long_url):
    """Call the URL shortener API to create a shortened URL"""
    try:
        response = requests.post(
            f"{base_url}/api/shorten", 
            json={"url": long_url},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('short_url')
        else:
            print(f"Error shortening URL: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def access_short_url(short_url):
    """Access a shortened URL to trigger the redirect"""
    try:
        response = requests.get(short_url, timeout=5, allow_redirects=False)
        if response.status_code == 302:
            return True
        else:
            print(f"Failed to redirect short URL: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def worker(base_url, request_count, report_queue):
    """Worker thread to make requests"""
    successful = 0
    failed = 0
    
    for _ in range(request_count):
        # Generate a random URL and try to shorten it
        long_url = generate_random_url()
        short_url = shorten_url(base_url, long_url)
        
        if short_url:
            successful += 1
            # Optionally access the short URL (adds more load)
            if random.choice([True, False]):
                if access_short_url(short_url):
                    successful += 1
                else:
                    failed += 1
        else:
            failed += 1
            
    report_queue.append((successful, failed))

def run_stress_test(base_url, num_threads, requests_per_thread, duration_seconds):
    """Run a stress test against the URL shortener service"""
    start_time = time.time()
    end_time = start_time + duration_seconds
    
    print(f"Starting stress test against {base_url}")
    print(f"Using {num_threads} threads, {requests_per_thread} requests per thread")
    print(f"Test will run for {duration_seconds} seconds")
    
    total_successful = 0
    total_failed = 0
    total_batches = 0
    
    try:
        while time.time() < end_time:
            report_queue = []
            
            # Create and start worker threads
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for _ in range(num_threads):
                    executor.submit(worker, base_url, requests_per_thread, report_queue)
            
            # Process results
            batch_successful = 0
            batch_failed = 0
            for successful, failed in report_queue:
                batch_successful += successful
                batch_failed += failed
            
            total_successful += batch_successful
            total_failed += batch_failed
            total_batches += 1
            
            print(f"Batch {total_batches} completed: {batch_successful} successful, {batch_failed} failed")
            
            # Sleep a bit to allow the system to process
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    # Print final statistics
    elapsed = time.time() - start_time
    total_requests = total_successful + total_failed
    requests_per_second = total_requests / elapsed if elapsed > 0 else 0
    
    print("\n=== Stress Test Results ===")
    print(f"Test duration: {elapsed:.2f} seconds")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {total_successful}")
    print(f"Failed requests: {total_failed}")
    print(f"Requests per second: {requests_per_second:.2f}")
    print(f"Success rate: {(total_successful / total_requests * 100) if total_requests > 0 else 0:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URL Shortener Stress Testing Tool")
    parser.add_argument("--url", required=True, help="Base URL of the shortener service (e.g., http://shortener.local)")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent threads")
    parser.add_argument("--requests", type=int, default=5, help="Requests per thread")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    
    args = parser.parse_args()
    
    run_stress_test(args.url, args.threads, args.requests, args.duration)