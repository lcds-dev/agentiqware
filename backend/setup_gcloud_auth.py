#!/usr/bin/env python3
"""
Script to setup Google Cloud authentication for development
"""

import os
import subprocess
import sys
from pathlib import Path

def check_gcloud_cli():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ gcloud CLI is installed")
            print(result.stdout.split('\n')[0])
            return True
    except FileNotFoundError:
        pass
    
    print("❌ gcloud CLI is not installed")
    print("Please install it from: https://cloud.google.com/sdk/docs/install")
    return False

def setup_application_default_credentials():
    """Setup Application Default Credentials"""
    try:
        print("🔑 Setting up Application Default Credentials...")
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'login'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Application Default Credentials configured successfully")
            return True
        else:
            print(f"❌ Error setting up credentials: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")
        return False

def check_firestore_access():
    """Test Firestore access with current credentials"""
    try:
        print("🔍 Testing Firestore access...")
        
        from google.cloud import firestore
        
        # Try to initialize Firestore client
        db = firestore.Client()
        
        # Try to access a collection (this will fail if no access)
        collections = db.collections()
        
        print("✅ Firestore access verified")
        return True
        
    except Exception as e:
        print(f"❌ Firestore access failed: {str(e)}")
        print("Make sure you have the correct project set and Firestore enabled")
        return False

def set_project():
    """Set the Google Cloud project"""
    project_id = input("Enter your Google Cloud Project ID (or press Enter for 'agentiqware-dev'): ").strip()
    
    if not project_id:
        project_id = "agentiqware-dev"
    
    try:
        result = subprocess.run(['gcloud', 'config', 'set', 'project', project_id], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Project set to: {project_id}")
            
            # Update .env file
            env_file = Path(__file__).parent / '.env'
            if env_file.exists():
                content = env_file.read_text()
                lines = content.split('\n')
                
                updated_lines = []
                project_updated = False
                firestore_updated = False
                
                for line in lines:
                    if line.startswith('PROJECT_ID='):
                        updated_lines.append(f'PROJECT_ID={project_id}')
                        project_updated = True
                    elif line.startswith('FIRESTORE_PROJECT_ID='):
                        updated_lines.append(f'FIRESTORE_PROJECT_ID={project_id}')
                        firestore_updated = True
                    else:
                        updated_lines.append(line)
                
                if not project_updated:
                    updated_lines.append(f'PROJECT_ID={project_id}')
                if not firestore_updated:
                    updated_lines.append(f'FIRESTORE_PROJECT_ID={project_id}')
                
                env_file.write_text('\n'.join(updated_lines))
                print(f"✅ Updated .env file with project ID")
            
            return True
        else:
            print(f"❌ Error setting project: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting project: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Google Cloud authentication for Agentiqware development")
    print("=" * 60)
    
    # Check if gcloud CLI is installed
    if not check_gcloud_cli():
        return 1
    
    # Set project
    if not set_project():
        return 1
    
    # Setup Application Default Credentials
    if not setup_application_default_credentials():
        print("⚠️  You can also manually run: gcloud auth application-default login")
        return 1
    
    # Test Firestore access
    if not check_firestore_access():
        print("⚠️  Firestore access failed. Make sure:")
        print("   1. The project has Firestore enabled")
        print("   2. Your account has Firestore permissions")
        print("   3. The project ID is correct")
        return 1
    
    print("\n🎉 Google Cloud authentication setup completed successfully!")
    print("You can now run the backend server with: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main())