#!/usr/bin/env python3
"""
Test script to verify analytics tracking is working
"""
import os
import json
import requests

# Test local analytics file creation
DATA_DIR = '/tmp/test_analytics'
LOCAL_ANALYTICS_FILE = os.path.join(DATA_DIR, 'local_analytics.json')

os.makedirs(DATA_DIR, exist_ok=True)

def update_local_analytics(push_type):
    """Update local analytics counter"""
    try:
        # Load existing counters
        if os.path.exists(LOCAL_ANALYTICS_FILE):
            with open(LOCAL_ANALYTICS_FILE, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = {'github_count': 0, 'dockerhub_count': 0}
        
        # Update counter
        if push_type == 'github':
            analytics['github_count'] = analytics.get('github_count', 0) + 1
        elif push_type == 'dockerhub':
            analytics['dockerhub_count'] = analytics.get('dockerhub_count', 0) + 1
        
        # Save updated counters
        with open(LOCAL_ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f)
        
        print(f"Updated local analytics: {push_type} count is now {analytics.get(push_type + '_count', 0)}")
        
    except Exception as e:
        print(f"Failed to update local analytics for {push_type}: {e}")

def get_local_analytics():
    """Get local analytics counters"""
    try:
        if os.path.exists(LOCAL_ANALYTICS_FILE):
            with open(LOCAL_ANALYTICS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load local analytics: {e}")
    
    return {'github_count': 0, 'dockerhub_count': 0}

# Test the functions
print("Testing local analytics...")
print("Initial counters:", get_local_analytics())

update_local_analytics('github')
update_local_analytics('dockerhub')
update_local_analytics('github')

print("Final counters:", get_local_analytics())

# Test external analytics API
ANALYTICS_API = 'https://hub-backend.satrawi.cc'
print(f"\nTesting external API: {ANALYTICS_API}")

# Test click endpoint
try:
    response = requests.post(
        f'{ANALYTICS_API}/click',
        json={
            'project_name': 'hub-helper',
            'push_type': 'github'
        },
        timeout=5
    )
    print(f"Click endpoint response: {response.status_code}")
    if response.text:
        print(f"Response body: {response.text}")
except Exception as e:
    print(f"Click endpoint error: {e}")

# Test stats endpoint
try:
    response = requests.get(f'{ANALYTICS_API}/stats/hub-helper', timeout=5)
    print(f"Stats endpoint response: {response.status_code}")
    if response.text:
        print(f"Response body: {response.text}")
except Exception as e:
    print(f"Stats endpoint error: {e}")

# Test alternative endpoints
alt_endpoints = [
    f'{ANALYTICS_API}/analytics/hub-helper',
    f'{ANALYTICS_API}/analytics',
    f'{ANALYTICS_API}/health'
]

for endpoint in alt_endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Data: {data}")
            except:
                print(f"  Text: {response.text[:100]}...")
    except Exception as e:
        print(f"{endpoint}: ERROR - {e}")
