# API Autocomplete Scraper

## Overview
This script fetches autocomplete suggestions from three different API versions (`v1`, `v2`, and `v3`). It implements a multi-threaded approach with adaptive rate limiting and ensures efficient exploration of potential queries to maximize unique name retrieval.

## Features
- **Supports Three API Versions:** Handles `v1`, `v2`, and `v3` requests simultaneously.
- **Multi-threaded Execution:** Uses `ThreadPoolExecutor` for concurrent API calls.
- **Rate Limiting with Backoff:** Adapts request frequency dynamically based on API responses.
- **Queue-based Exploration:** Efficiently explores prefixes to discover new names.
- **Error Handling & Logging:** Handles API errors, exceptions, and rate limit responses.
- **JSON Output:** Saves extracted names into separate JSON files for each API version.

## How It Works
1. **API Requests:**
   - The script makes requests to the API endpoints using predefined query prefixes.
   - If a response is successful, the script extracts names from the `results` field.
   
2. **Rate Limiting & Backoff:**
   - Initially, requests are spaced at `0.2s` intervals.
   - On successful responses, the rate limit is adjusted to be more aggressive.
   - If a `429 Too Many Requests` error is encountered, the request backs off exponentially up to `5s`.

3. **Exploration Strategy:**
   - Uses a queue to store query prefixes.
   - Initially enqueues all lowercase letters (`a-z`).
   - If a new name is found, it enqueues extended prefixes for further search.
   - Ensures no duplicate queries are sent to the same API.

4. **Multi-threading:**
   - Each API version runs in a separate thread.
   - The script manages synchronization using Python's `threading.Lock`.
   
5. **Data Storage:**
   - Extracted names are stored in `api_results` dictionary.
   - Results are saved in separate JSON files (`extracted_names_v1.json`, `extracted_names_v2.json`, etc.).

## Dependencies
- Python 3.x
- `requests`
- `concurrent.futures`
- `threading`
- `queue`
- `json`
- `time`

## Running the Script
To execute the script, ensure all dependencies are installed, then run:
```sh
python3 script.py
```

## Output
- The script prints discovered names in real-time.
- The final results, including total requests made and names found, are displayed.
- JSON files are saved with extracted names for each API version.

## Future Enhancements
- Implement caching to avoid redundant API calls.
- Use asyncio for better efficiency with high concurrency.
- Store extracted names in a database for further analysis.