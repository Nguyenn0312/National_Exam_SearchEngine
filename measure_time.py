import requests
import time

# The URL you are testing (using your filter endpoint)
url = "http://localhost:8000/api/filter/?math=10"

print("--- Starting 10-Request Performance Test ---")
print(f"Target URL: {url}\n")

durations = []

for i in range(1, 11):
    print(f"Sending Request {i}...", end=" ", flush=True)
    
    start_time = time.time()
    try:
        response = requests.get(url)
        end_time = time.time()
        
        duration = end_time - start_time
        durations.append(duration)
        
        print(f"Done! ({duration:.4f}s) | Status: {response.status_code}")
    except Exception as e:
        print(f"Failed! Error: {e}")

# --- FINAL ANALYSIS ---
if durations:
    avg_time = sum(durations) / len(durations)
    max_time = max(durations)
    min_time = min(durations)

    print("\n--- FINAL RESULTS ---")
    print(f"Total Requests:    {len(durations)}")
    print(f"Fastest Request:   {min_time:.4f} seconds")
    print(f"Slowest Request:   {max_time:.4f} seconds")
    print(f"Average Time:      {avg_time:.4f} seconds")
    print("----------------------")
else:
    print("\nNo successful requests were completed.")