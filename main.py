import requests
import time
import json
import threading
import queue
import concurrent.futures

# Base API URLs for v1, v2, and v3
BASE_URLS = {
    "v1": "http://35.200.185.69:8000/v1/autocomplete?query=",
    "v2": "http://35.200.185.69:8000/v2/autocomplete?query=",
    "v3": "http://35.200.185.69:8000/v3/autocomplete?query="
}

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Adaptive rate limit settings
INITIAL_RATE_LIMIT = 0.2
MAX_RATE_LIMIT = 5
rate_limits = {version: INITIAL_RATE_LIMIT for version in BASE_URLS.keys()}

# Shared storage
api_results = {
    "v1": {"names": set(), "requests": 0},
    "v2": {"names": set(), "requests": 0},
    "v3": {"names": set(), "requests": 0}
}

# Track visited prefixes to prevent redundant API calls
explored_prefixes = {version: set() for version in BASE_URLS.keys()}

# Thread synchronization tools
lock = threading.Lock()
prefix_queues = {version: queue.Queue() for version in BASE_URLS.keys()}


def fetch_names(api_version, query, retry_count=0):
    url = BASE_URLS[api_version] + query

    try:
        response = requests.get(url, headers=HEADERS)
        
        with lock:
            api_results[api_version]["requests"] += 1

        if response.status_code == 200:
            with lock:
                rate_limits[api_version] = max(rate_limits[api_version] / 2, INITIAL_RATE_LIMIT)
            return response.json().get("results", [])

        elif response.status_code == 429:
            wait_time = min(2 ** retry_count, MAX_RATE_LIMIT)
            print(f"[{api_version}] Rate limit hit! Retrying after {wait_time:.2f}s...")
            time.sleep(wait_time)
            return fetch_names(api_version, query, retry_count + 1)

        else:
            print(f"[{api_version}] Error {response.status_code}: {response.text}")
            return []

    except Exception as e:
        print(f"[{api_version}] Exception occurred: {e}")
        return []


def explore_names(api_version):
    while not prefix_queues[api_version].empty():
        query_prefix = prefix_queues[api_version].get()

        with lock:
            if query_prefix in explored_prefixes[api_version]:
                continue
            explored_prefixes[api_version].add(query_prefix)

        names = fetch_names(api_version, query_prefix)

        with lock:
            for name in names:
                if name not in api_results[api_version]["names"]:
                    api_results[api_version]["names"].add(name)
                    print(f"[{api_version}] Found: {name}")
                    
                    # Push new prefixes for deeper search
                    if len(name) > len(query_prefix):
                        prefix_queues[api_version].put(name[:len(query_prefix) + 1])

        time.sleep(rate_limits[api_version])


# Initialize queues with starting characters
for version in BASE_URLS.keys():
    for letter in "abcdefghijklmnopqrstuvwxyz":
        prefix_queues[version].put(letter)

# Multi-threaded execution with controlled concurrency
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(explore_names, version) for version in BASE_URLS.keys()]
    concurrent.futures.wait(futures)

# Save results for each API version
for version in BASE_URLS.keys():
    filename = f"extracted_names_{version}.json"
    with open(filename, "w") as f:
        json.dump(list(api_results[version]["names"]), f, indent=4)
    print(f" Saved {len(api_results[version]['names'])} names from {version} to {filename}")

# Print final statistics
print("\n FINAL RESULTS:")
for version in BASE_URLS.keys():
    print(f"[{version}] Requests Made: {api_results[version]['requests']}, Names Found: {len(api_results[version]['names'])}")
