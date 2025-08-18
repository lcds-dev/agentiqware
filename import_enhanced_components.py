#!/usr/bin/env python3
"""
Script to import enhanced components to Firestore
"""

import json
import sys
import os
from google.cloud import firestore
from typing import List, Dict, Any

def import_components_to_firestore(json_file_path: str) -> int:
    """Import enhanced components from JSON file to Firestore"""
    
    try:
        # Initialize Firestore client
        print("Initializing Firestore client...")
        
        # Try to get project ID from environment
        project_id = os.environ.get('PROJECT_ID') or os.environ.get('FIRESTORE_PROJECT_ID')
        if project_id:
            print(f"Using project ID: {project_id}")
            db = firestore.Client(project=project_id)
        else:
            print("Using default project from Application Default Credentials")
            db = firestore.Client()
        
        # Test connection
        print("Testing Firestore connection...")
        test_collection = db.collection('components')
        # This will raise an exception if connection fails
        list(test_collection.limit(1).stream())
        print("✅ Firestore connection successful")
        
        # Read the enhanced components JSON
        print(f"Reading components from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            components = json.load(f)
        
        print(f"Found {len(components)} components to import")
        
        # Validate components structure
        print("Validating components structure...")
        validated_components = []
        validation_errors = []
        
        for i, component in enumerate(components):
            try:
                # Check required fields
                required_fields = ['actionName', 'actionLabel', 'actionGroup', 'status']
                missing_fields = [field for field in required_fields if not component.get(field)]
                
                if missing_fields:
                    validation_errors.append(f"Component {i+1}: Missing required fields: {missing_fields}")
                    continue
                
                # Ensure ai_metadata exists
                if 'ai_metadata' not in component:
                    component['ai_metadata'] = {
                        'natural_language_description': component.get('actionDescription', ''),
                        'intent_keywords': [],
                        'use_cases': [],
                        'complexity_level': 'basic'
                    }
                
                validated_components.append(component)
                
            except Exception as e:
                validation_errors.append(f"Component {i+1}: Validation error: {str(e)}")
        
        if validation_errors:
            print(f"⚠️  Found {len(validation_errors)} validation errors:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more errors")
        
        print(f"✅ {len(validated_components)} components validated successfully")
        
        # Get reference to components collection
        components_ref = db.collection('components')
        
        # Track import statistics
        imported_count = 0
        updated_count = 0
        errors = []
        
        # Process in batches for better performance
        batch_size = 50
        batch = db.batch()
        operations_in_batch = 0
        
        for i, component in enumerate(validated_components):
            try:
                print(f"Processing component {i+1}/{len(validated_components)}: {component.get('actionName', 'unknown')}")
                
                # Check if component already exists by actionName
                existing_query = components_ref.where('actionName', '==', component.get('actionName')).limit(1)
                existing_docs = list(existing_query.stream())
                
                if existing_docs:
                    # Update existing component
                    doc_ref = existing_docs[0].reference
                    batch.update(doc_ref, component)
                    updated_count += 1
                    print(f"  [✓] Queued update for: {component.get('actionName')}")
                else:
                    # Create new component
                    doc_ref = components_ref.document()
                    batch.set(doc_ref, component)
                    imported_count += 1
                    print(f"  [✓] Queued creation for: {component.get('actionName')}")
                
                operations_in_batch += 1
                
                # Commit batch when it reaches batch_size or at the end
                if operations_in_batch >= batch_size or i == len(validated_components) - 1:
                    print(f"  [⚡] Committing batch of {operations_in_batch} operations...")
                    batch.commit()
                    batch = db.batch()
                    operations_in_batch = 0
                
            except Exception as e:
                error_msg = f"Failed to process component {component.get('actionName', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                print(f"  [✗] {error_msg}")
        
        # Print summary
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Total components processed: {len(components)}")
        print(f"Components validated: {len(validated_components)}")
        print(f"New components created: {imported_count}")
        print(f"Existing components updated: {updated_count}")
        print(f"Validation errors: {len(validation_errors)}")
        print(f"Import errors: {len(errors)}")
        
        if errors:
            print("\nImport Errors:")
            for error in errors:
                print(f"  - {error}")
        
        print(f"\n[SUCCESS] Import completed successfully!")
        print(f"Components are now available in Firestore and ready for dynamic loading")
        print(f"Total components in Firestore: {imported_count + updated_count}")
        
    except Exception as e:
        print(f"\n[ERROR] Error during import: {str(e)}")
        return 1
    
    return 0

def verify_firestore_setup():
    """Verify that Firestore is properly configured"""
    try:
        print("Verifying Firestore connection...")
        db = firestore.Client()
        
        # Try to read from components collection
        components_ref = db.collection('components')
        docs = list(components_ref.limit(1).stream())
        
        print("[✓] Firestore connection verified")
        return True
        
    except Exception as e:
        print(f"[✗] Firestore connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Google Cloud credentials are configured:")
        print("   gcloud auth application-default login")
        print("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("3. Verify project has Firestore enabled")
        return False

def main():
    """Main execution function"""
    
    print("Enhanced Components Firestore Import Tool")
    print("=" * 50)
    
    # Verify Firestore setup
    if not verify_firestore_setup():
        return 1
    
    # Default path to enhanced components
    default_path = "enhanced_components_full.json"
    json_file_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"Error: File not found: {json_file_path}")
        print(f"Usage: python {sys.argv[0]} [path_to_components.json]")
        return 1
    
    # Confirm before proceeding
    print(f"\nThis will import/update components from: {json_file_path}")
    print("This operation will modify your Firestore database.")
    
    confirm = input("\nDo you want to continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Import cancelled by user")
        return 0
    
    # Import components
    return import_components_to_firestore(json_file_path)

if __name__ == "__main__":
    exit(main())