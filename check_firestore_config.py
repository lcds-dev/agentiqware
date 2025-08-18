#!/usr/bin/env python3
"""
Check current Firestore configuration
"""

import os
from google.cloud import firestore

def check_firestore_config():
    """Check current Firestore configuration"""
    
    print("🔍 Checking Firestore Configuration")
    print("=" * 50)
    
    # Check environment variables
    project_id_env = os.environ.get('PROJECT_ID')
    firestore_project_env = os.environ.get('FIRESTORE_PROJECT_ID')
    
    print(f"📁 PROJECT_ID (env): {project_id_env}")
    print(f"🔥 FIRESTORE_PROJECT_ID (env): {firestore_project_env}")
    
    # Try to connect to Firestore
    try:
        # Without explicit project (uses default credentials)
        print("\n🔗 Testing connection with default credentials...")
        db_default = firestore.Client()
        print(f"✅ Default project: {db_default.project}")
        
        # Test collection access
        components_ref = db_default.collection('components')
        docs = list(components_ref.limit(1).stream())
        print(f"📊 Components collection accessible: {len(docs) >= 0}")
        
        if len(docs) > 0:
            print(f"📄 Sample component found: {docs[0].id}")
        else:
            print("📄 No components found in collection")
        
    except Exception as e:
        print(f"❌ Error connecting to Firestore: {e}")
    
    # Try with explicit project from env
    if firestore_project_env:
        try:
            print(f"\n🔗 Testing connection with project: {firestore_project_env}...")
            db_explicit = firestore.Client(project=firestore_project_env)
            print(f"✅ Explicit project: {db_explicit.project}")
        except Exception as e:
            print(f"❌ Error with explicit project: {e}")

if __name__ == "__main__":
    # Manually set environment for this test
    os.environ['PROJECT_ID'] = 'agentiqware-dev'
    os.environ['FIRESTORE_PROJECT_ID'] = 'agentiqware-dev'
    
    check_firestore_config()