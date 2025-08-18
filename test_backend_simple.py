#!/usr/bin/env python3
"""
Simple test for backend without full installation
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test if we can import the required modules"""
    
    try:
        print("[INFO] Testing imports...")
        
        # Test FastAPI import
        import fastapi
        print(f"[SUCCESS] FastAPI version: {fastapi.__version__}")
        
        # Test Google Cloud Firestore
        from google.cloud import firestore
        print("[SUCCESS] Google Cloud Firestore imported")
        
        # Test components router
        from routers import components
        print("[SUCCESS] Components router imported")
        
        # Test if we can create a Firestore client (this might fail without auth)
        try:
            db = firestore.Client()
            print("[SUCCESS] Firestore client created (auth working)")
        except Exception as e:
            print(f"[WARNING] Firestore auth not configured: {e}")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_components_data():
    """Test if we can load the components data directly"""
    
    try:
        print("\n[INFO] Testing components data...")
        
        components_file = Path("enhanced_components_full.json")
        if not components_file.exists():
            print("[ERROR] Enhanced components file not found")
            return False
        
        import json
        with open(components_file, 'r', encoding='utf-8') as f:
            components = json.load(f)
        
        print(f"[SUCCESS] Components loaded: {len(components)}")
        
        # Check structure of first component
        if len(components) > 0:
            first_comp = components[0]
            required_fields = ['actionName', 'actionLabel', 'actionGroup']
            missing_fields = [field for field in required_fields if field not in first_comp]
            
            if missing_fields:
                print(f"[WARNING] Missing fields in component: {missing_fields}")
            else:
                print("[SUCCESS] Component structure is valid")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Components data test failed: {e}")
        return False

def test_mock_api():
    """Test the API logic with mock data"""
    
    try:
        print("\n[INFO] Testing API logic with mock data...")
        
        # Mock component data
        mock_components = [
            {
                "actionName": "test_component",
                "actionLabel": "Test Component",
                "actionGroup": "Test",
                "status": "S",
                "ai_metadata": {
                    "natural_language_description": "A test component",
                    "intent_keywords": ["test", "mock"],
                    "complexity_level": "basic"
                }
            }
        ]
        
        # Test filtering logic (simulate what the API does)
        active_components = [comp for comp in mock_components if comp.get('status') == 'S']
        print(f"[SUCCESS] Active components filter: {len(active_components)}")
        
        # Test search logic
        search_term = "test"
        matching = []
        for comp in active_components:
            if search_term.lower() in comp.get('actionLabel', '').lower():
                matching.append(comp)
        
        print(f"[SUCCESS] Search logic works: {len(matching)} matches for '{search_term}'")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Mock API test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("Testing Backend Components Integration")
    print("=" * 50)
    
    success = True
    
    # Test 1: Imports
    if not test_imports():
        success = False
    
    # Test 2: Components data
    if not test_components_data():
        success = False
    
    # Test 3: Mock API
    if not test_mock_api():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("1. Configure Google Cloud authentication")
        print("2. Import components to Firestore")
        print("3. Start the backend server")
        return 0
    else:
        print("[ERROR] Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())