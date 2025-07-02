#!/usr/bin/env python3
"""
Script to reset analytics counters to zero
"""
import os
import json
import requests

# Configuration
ANALYTICS_API = 'https://hub-backend.satrawi.cc'
DATA_DIR = '/app/data'
LOCAL_ANALYTICS_FILE = os.path.join(DATA_DIR, 'local_analytics.json')

def reset_external_analytics():
    """Reset external analytics API counters"""
    print("Resetting external analytics API...")
    try:
        # Check if there's a reset endpoint
        response = requests.post(
            f'{ANALYTICS_API}/reset',
            json={'project_name': 'hub-helper'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ External analytics reset successfully")
            return True
        else:
            print(f"❌ External API reset failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ External API reset error: {e}")
        return False

def reset_local_analytics():
    """Reset local analytics file"""
    print("Resetting local analytics...")
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Reset counters to zero
        analytics = {'github_count': 0, 'dockerhub_count': 0}
        
        with open(LOCAL_ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f, indent=2)
        
        print(f"✅ Local analytics reset successfully: {analytics}")
        return True
    except Exception as e:
        print(f"❌ Local analytics reset error: {e}")
        return False

def verify_reset():
    """Verify that counters are reset"""
    print("\nVerifying reset...")
    
    # Check external API
    try:
        response = requests.get(f'{ANALYTICS_API}/analytics/hub-helper', timeout=5)
        if response.status_code == 200:
            data = response.json()
            github_count = data.get('github_clicks', 0)
            docker_count = data.get('dockerhub_clicks', 0)
            print(f"External API - GitHub: {github_count}, Docker Hub: {docker_count}")
        else:
            print(f"External API check failed: {response.status_code}")
    except Exception as e:
        print(f"External API check error: {e}")
    
    # Check local analytics
    try:
        if os.path.exists(LOCAL_ANALYTICS_FILE):
            with open(LOCAL_ANALYTICS_FILE, 'r') as f:
                local = json.load(f)
            print(f"Local analytics - GitHub: {local.get('github_count', 0)}, Docker Hub: {local.get('dockerhub_count', 0)}")
        else:
            print("Local analytics file does not exist")
    except Exception as e:
        print(f"Local analytics check error: {e}")

if __name__ == "__main__":
    print("🔄 Resetting Hub Helper Analytics Counters...")
    print("=" * 50)
    
    # Reset both external and local analytics
    external_success = reset_external_analytics()
    local_success = reset_local_analytics()
    
    print("\n" + "=" * 50)
    if external_success and local_success:
        print("✅ All counters reset successfully!")
    elif local_success:
        print("⚠️  Local counters reset, but external API reset failed")
        print("   You may need to reset the external API manually")
    else:
        print("❌ Counter reset failed")
    
    # Verify the reset
    verify_reset()
