import asyncio
import httpx
import time
import random
from datetime import datetime
import sys

# --- Laptop Optimized Configuration ---
BASE_URL = "http://localhost:3000"
TOTAL_USERS = 10         # Best for a single machine
CONCURRENCY_LIMIT = 50     # Avoids socket exhaustion on Windows/Mac
ACTIONS_PER_USER = 1      # More actions per user to test data growth

class StressTestResult:
    def __init__(self):
        self.success = 0
        self.failure = 0
        self.latencies = []
        self.start_time = time.time()

    def log(self, success, latency):
        if success:
            self.success += 1
        else:
            self.failure += 1
        if latency > 0:
            self.latencies.append(latency)

    def report(self):
        total = self.success + self.failure
        if total == 0: return "No data."
        
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0
        p95_latency = sorted(self.latencies)[int(len(self.latencies) * 0.95)] if self.latencies else 0
        
        duration = time.time() - self.start_time
        
        return f"""
================ LAPTOP STRESS TEST REPORT ================
Test Duration:      {duration:.2f}s
Total Users:        {TOTAL_USERS}
Total Requests:     {total}
Throughput:         {total / duration:.2f} req/s

Status:
  - Successful:     {self.success} ({(self.success/total)*100:.1f}%)
  - Failed:         {self.failure} ({(self.failure/total)*100:.1f}%)

Latency (Response Time):
  - Average:        {avg_latency*1000:.2f}ms
  - 95th Percentile: {p95_latency*1000:.2f}ms
  - Maximum:        {max_latency*1000:.2f}ms
===========================================================
"""

results = StressTestResult()
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

async def run_user_scenario(client, user_id):
    """
    Simulates a heavy user workload:
    Register -> Login -> Create 10 Contacts -> List Contacts -> Delete 1 Contact
    """
    email = f"user_{user_id}_{int(time.time() * 1000)}@laptop-stress.com"
    password = "password123"
    
    try:
        # 1. Register (Limited by semaphore)
        async with semaphore:
            start = time.time()
            resp = await client.post(f"{BASE_URL}/api/register", json={
                "name": f"Stress User {user_id}",
                "email": email,
                "password": password
            })
            results.log(resp.status_code == 200, time.time() - start)
        
        # 2. Login
        async with semaphore:
            start = time.time()
            resp = await client.post(f"{BASE_URL}/api/login", json={
                "email": email,
                "password": password
            })
            results.log(resp.status_code == 200, time.time() - start)
            
        if resp.status_code != 200: return
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        last_contact_id = None

        # 3. Heavy Actions (Create contacts)
        for i in range(ACTIONS_PER_USER):
            async with semaphore:
                start = time.time()
                resp = await client.post(f"{BASE_URL}/api/contacts", 
                    headers=headers,
                    json={
                        "name": f"Contact {user_id}_{i}",
                        "email": f"c_{user_id}_{i}@stress.com",
                        "status": "Lead",
                        "tags": ["stress-test", "auto-generated"]
                    }
                )
                if resp.status_code == 200:
                    last_contact_id = resp.json().get("id")
                results.log(resp.status_code == 200, time.time() - start)
            
            # Simulated sleep
            await asyncio.sleep(random.uniform(0.05, 0.2))

        # 4. List Contacts
        async with semaphore:
            start = time.time()
            resp = await client.get(f"{BASE_URL}/api/contacts", headers=headers)
            results.log(resp.status_code == 200, time.time() - start)

        # 5. Cleanup (Delete the last created contact)
        if last_contact_id:
            async with semaphore:
                start = time.time()
                resp = await client.delete(f"{BASE_URL}/api/contacts/{last_contact_id}", headers=headers)
                results.log(resp.status_code == 200, time.time() - start)

    except Exception:
        results.log(False, 0)

async def main():
    print("\nStarting Laptop Optimized Stress Test...")
    print(f"   Target: {TOTAL_USERS} users | {ACTIONS_PER_USER} actions each")
    print(f"   Max Concurrency: {CONCURRENCY_LIMIT}")
    print("   -------------------------------------------")
    
    results.start_time = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = []
        for i in range(TOTAL_USERS):
            tasks.append(run_user_scenario(client, i))
            
            # Progress visualization
            if i % 50 == 0:
                sys.stdout.write(f"\rInitializing Users: {i}/{TOTAL_USERS}...")
                sys.stdout.flush()
                await asyncio.sleep(0.01)
        
        print("\rInitializing Users: Done. Running load...")
        await asyncio.gather(*tasks)
    
    print(results.report())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
