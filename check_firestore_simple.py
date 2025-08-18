#!/usr/bin/env python3
"""
Simple check for Firestore configuration
"""

import os
from google.cloud import firestore

def main():
    """Check Firestore configuration"""
    
    print("Checking Firestore Configuration")
    print("=" * 40)
    
    try:
        # Connect to Firestore
        print("Connecting to Firestore...")
        db = firestore.Client()
        print(f"Connected to project: {db.project}")
        
        # Test components collection
        print("Testing components collection...")
        components_ref = db.collection('components')
        docs = list(components_ref.limit(5).stream())
        
        print(f"Components found: {len(docs)}")
        
        if len(docs) > 0:
            print("Sample components:")
            for i, doc in enumerate(docs):
                data = doc.to_dict()
                print(f"  {i+1}. {data.get('actionName', 'unknown')} ({data.get('actionGroup', 'unknown')})")
        else:
            print("No components found in Firestore")
            print("You may need to import components first:")
            print("  python import_enhanced_components.py")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if you're authenticated: gcloud auth list")
        print("2. Check current project: gcloud config get-value project")
        print("3. Make sure Firestore is enabled in your project")
        return 1

if __name__ == "__main__":
    exit(main())