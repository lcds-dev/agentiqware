#!/usr/bin/env python3
"""
Complete setup script for Firestore connection in Agentiqware
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main setup process"""
    print("Setting up complete Firestore connection for Agentiqware")
    print("=" * 70)
    
    # Step 1: Setup Google Cloud Authentication
    print("\nStep 1: Google Cloud Authentication")
    print("-" * 40)
    
    auth_script = Path("backend/setup_gcloud_auth.py")
    if auth_script.exists():
        print("Running Google Cloud authentication setup...")
        result = subprocess.run([sys.executable, str(auth_script)], cwd=".")
        if result.returncode != 0:
            print("[ERROR] Google Cloud authentication setup failed")
            return 1
    else:
        print("[WARNING] Google Cloud auth script not found. Please run manually:")
        print("   cd backend && python setup_gcloud_auth.py")
    
    # Step 2: Install Backend Dependencies
    print("\nStep 2: Installing Backend Dependencies")
    print("-" * 40)
    
    backend_dir = Path("backend")
    if backend_dir.exists():
        requirements_file = backend_dir / "requirements.txt"
        if requirements_file.exists():
            print("Installing Python dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], cwd=str(backend_dir))
            
            if result.returncode == 0:
                print("[SUCCESS] Backend dependencies installed successfully")
            else:
                print("[ERROR] Failed to install backend dependencies")
                return 1
        else:
            print("[WARNING] requirements.txt not found in backend directory")
    
    # Step 3: Check Enhanced Components File
    print("\nStep 3: Checking Enhanced Components File")
    print("-" * 40)
    
    components_file = Path("enhanced_components_full.json")
    if components_file.exists():
        print(f"[SUCCESS] Enhanced components file found: {components_file}")
        
        # Get file size
        file_size = components_file.stat().st_size
        print(f"   File size: {file_size:,} bytes")
        
        # Try to load and validate
        try:
            import json
            with open(components_file, 'r', encoding='utf-8') as f:
                components = json.load(f)
            print(f"   Components count: {len(components)}")
            print("[SUCCESS] Enhanced components file is valid JSON")
        except Exception as e:
            print(f"[ERROR] Error reading components file: {e}")
            return 1
    else:
        print("[WARNING] Enhanced components file not found")
        print("   Please run: python enhance_all_components.py")
        return 1
    
    # Step 4: Import Components to Firestore
    print("\nStep 4: Importing Components to Firestore")
    print("-" * 40)
    
    import_script = Path("import_enhanced_components.py")
    if import_script.exists():
        print("Starting component import to Firestore...")
        
        # Set up environment for the import
        env = os.environ.copy()
        env_file = Path("backend/.env")
        if env_file.exists():
            print("Loading environment variables from backend/.env")
            from dotenv import load_dotenv
            load_dotenv(str(env_file))
        
        result = subprocess.run([sys.executable, str(import_script)], cwd=".")
        if result.returncode == 0:
            print("[SUCCESS] Components imported to Firestore successfully")
        else:
            print("[ERROR] Component import failed")
            return 1
    else:
        print("[WARNING] Import script not found")
        return 1
    
    # Step 5: Test Backend API
    print("\nStep 5: Testing Backend API")
    print("-" * 40)
    
    print("Starting backend server for testing...")
    print("You can test the API endpoints:")
    print("   GET http://localhost:8080/api/components/")
    print("   GET http://localhost:8080/api/components/categories/")
    print("   GET http://localhost:8080/api/components/search/excel")
    print("")
    print("To start the backend server, run:")
    print("   cd backend && python main.py")
    
    # Step 6: Frontend Integration
    print("\nStep 6: Frontend Integration")
    print("-" * 40)
    
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        print("Frontend directory found")
        print("The components service is already configured to:")
        print("   1. Try loading from backend API (http://localhost:8080/api/components)")
        print("   2. Fallback to enhanced_components_full.json")
        print("   3. Fallback to hardcoded components")
        print("")
        print("To start the frontend, run:")
        print("   cd frontend && npm start")
    else:
        print("[WARNING] Frontend directory not found")
    
    print("\nSetup Complete!")
    print("=" * 70)
    print("Your Firestore connection is now configured.")
    print("")
    print("Next steps:")
    print("1. Start the backend: cd backend && python main.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Components will now load dynamically from Firestore!")
    print("")
    print("Troubleshooting:")
    print("- Check backend/.env for correct project configuration")
    print("- Verify Google Cloud credentials: gcloud auth list")
    print("- Ensure Firestore is enabled in your GCP project")
    
    return 0

if __name__ == "__main__":
    try:
        # Install required packages for this script
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], 
                      capture_output=True)
        exit(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Setup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        exit(1)