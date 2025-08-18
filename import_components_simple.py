#!/usr/bin/env python3
"""
Simple script to import enhanced components to Firestore
"""

import json
import os
from google.cloud import firestore

def import_components():
    """Import components to Firestore"""
    
    print("Enhanced Components Import to Firestore")
    print("=" * 50)
    
    try:
        # Initialize Firestore
        print("Connecting to Firestore...")
        db = firestore.Client()
        print(f"Connected to project: {db.project}")
        
        # Read components file
        components_file = "enhanced_components_full.json"
        print(f"Reading components from: {components_file}")
        
        with open(components_file, 'r', encoding='utf-8') as f:
            components = json.load(f)
        
        print(f"Found {len(components)} components to import")
        
        # Get components collection
        components_ref = db.collection('components')
        
        # Import in batches
        batch_size = 50
        imported = 0
        updated = 0
        
        for i in range(0, len(components), batch_size):
            batch = db.batch()
            batch_components = components[i:i + batch_size]
            
            print(f"Processing batch {i//batch_size + 1} ({len(batch_components)} components)...")
            
            for component in batch_components:
                # Check if exists
                existing_query = components_ref.where('actionName', '==', component.get('actionName')).limit(1)
                existing_docs = list(existing_query.stream())
                
                if existing_docs:
                    # Update existing
                    doc_ref = existing_docs[0].reference
                    batch.update(doc_ref, component)
                    updated += 1
                else:
                    # Create new
                    doc_ref = components_ref.document()
                    batch.set(doc_ref, component)
                    imported += 1
            
            # Commit batch
            batch.commit()
            print(f"Batch committed: {len(batch_components)} components processed")
        
        print("\n" + "=" * 50)
        print("IMPORT SUMMARY")
        print("=" * 50)
        print(f"Total components: {len(components)}")
        print(f"New components created: {imported}")
        print(f"Existing components updated: {updated}")
        print(f"Total in Firestore: {imported + updated}")
        print("\nImport completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"Error during import: {e}")
        return 1

if __name__ == "__main__":
    exit(import_components())