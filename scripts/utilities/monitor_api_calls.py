"""
Monitor API Calls in Real-Time
Shows recent API requests and statistics.
"""

import json
import os
from datetime import datetime
from collections import defaultdict


def monitor_api_calls():
    """Display API call statistics and recent requests."""
    
    log_file = "logs/api_requests.log"
    
    print("=" * 70)
    print("API CALL MONITOR")
    print("=" * 70)
    
    if not os.path.exists(log_file):
        print(f"\n⚠ No API request log found at: {log_file}")
        print("Make some predictions to generate API calls.")
        return
    
    # Read all log entries
    requests = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    requests.append(json.loads(line.strip()))
                except:
                    pass
    except Exception as e:
        print(f"✗ Error reading log: {e}")
        return
    
    if not requests:
        print("\n⚠ No API requests logged yet.")
        return
    
    # Calculate statistics
    total = len(requests)
    successful = sum(1 for r in requests if r.get('success'))
    failed = total - successful
    
    providers = defaultdict(int)
    models = defaultdict(int)
    endpoints = defaultdict(int)
    
    for req in requests:
        providers[req.get('provider', 'Unknown')] += 1
        models[req.get('model', 'Unknown')] += 1
        endpoints[req.get('endpoint', 'Unknown')] += 1
    
    # Display statistics
    print(f"\n📊 STATISTICS")
    print("-" * 70)
    print(f"Total Requests:     {total}")
    print(f"Successful:         {successful} ({successful/total*100:.1f}%)")
    print(f"Failed:             {failed} ({failed/total*100:.1f}%)")
    
    print(f"\n🔌 BY PROVIDER")
    print("-" * 70)
    for provider, count in sorted(providers.items(), key=lambda x: -x[1]):
        print(f"{provider:20} {count:5} requests")
    
    print(f"\n🤖 BY MODEL")
    print("-" * 70)
    for model, count in sorted(models.items(), key=lambda x: -x[1]):
        print(f"{model:40} {count:5} requests")
    
    print(f"\n📍 BY ENDPOINT")
    print("-" * 70)
    for endpoint, count in sorted(endpoints.items(), key=lambda x: -x[1]):
        print(f"{endpoint:30} {count:5} requests")
    
    # Display recent requests
    print(f"\n📝 RECENT REQUESTS (Last 10)")
    print("-" * 70)
    
    recent = requests[-10:]
    for req in recent:
        timestamp = req.get('timestamp', 'Unknown')
        provider = req.get('provider', 'Unknown')
        model = req.get('model', 'Unknown')[:30]
        success = "✓" if req.get('success') else "✗"
        session_count = req.get('session_count', '?')
        
        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp[:8] if len(timestamp) > 8 else timestamp
        
        print(f"{time_str} | {success} | #{session_count:3} | {provider:12} | {model}")
    
    print("\n" + "=" * 70)
    print(f"Log file: {log_file}")
    print("=" * 70)


if __name__ == "__main__":
    monitor_api_calls()
