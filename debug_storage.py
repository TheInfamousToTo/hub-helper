#!/usr/bin/env python3
"""
Debug script for Hub Helper persistent storage
Run this inside the container to check credentials storage
"""

import os
import json
from cryptography.fernet import Fernet

DATA_DIR = '/app/data'
CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')
KEY_FILE = os.path.join(DATA_DIR, 'key.key')

def check_storage():
    print("🔍 Hub Helper - Persistent Storage Debug")
    print("=" * 50)
    
    # Check data directory
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"   Exists: {os.path.exists(DATA_DIR)}")
    if os.path.exists(DATA_DIR):
        print(f"   Permissions: {oct(os.stat(DATA_DIR).st_mode)[-3:]}")
        print(f"   Contents: {os.listdir(DATA_DIR)}")
    
    # Check key file
    print(f"\n🔑 Key file: {KEY_FILE}")
    print(f"   Exists: {os.path.exists(KEY_FILE)}")
    if os.path.exists(KEY_FILE):
        print(f"   Size: {os.path.getsize(KEY_FILE)} bytes")
    
    # Check credentials file
    print(f"\n📄 Credentials file: {CREDENTIALS_FILE}")
    print(f"   Exists: {os.path.exists(CREDENTIALS_FILE)}")
    
    if os.path.exists(CREDENTIALS_FILE) and os.path.exists(KEY_FILE):
        try:
            # Try to decrypt and show structure (without sensitive data)
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
            
            with open(CREDENTIALS_FILE, 'r') as f:
                encrypted_data = f.read()
            
            f = Fernet(key)
            decrypted_data = json.loads(f.decrypt(encrypted_data.encode()).decode())
            
            print(f"   Decryption: ✅ Success")
            print(f"   Contains GitHub token: {'github_token' in decrypted_data}")
            print(f"   Contains Docker Hub creds: {'dockerhub_credentials' in decrypted_data}")
            
            if 'dockerhub_credentials' in decrypted_data:
                print(f"   Docker Hub username: {decrypted_data['dockerhub_credentials'].get('username', 'N/A')}")
                
        except Exception as e:
            print(f"   Decryption: ❌ Failed - {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    check_storage()
