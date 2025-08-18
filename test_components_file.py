#!/usr/bin/env python3
"""
Simple test to validate enhanced components file
"""

import json
from pathlib import Path

def test_components_file():
    """Test the enhanced components file"""
    
    components_file = Path("enhanced_components_full.json")
    
    if not components_file.exists():
        print("[ERROR] Enhanced components file not found")
        return 1
    
    try:
        print(f"[INFO] Reading file: {components_file}")
        with open(components_file, 'r', encoding='utf-8') as f:
            components = json.load(f)
        
        print(f"[SUCCESS] File is valid JSON")
        print(f"[INFO] Components count: {len(components)}")
        
        if len(components) > 0:
            first_component = components[0]
            print(f"[INFO] First component: {first_component.get('actionName', 'unknown')}")
            print(f"[INFO] Has AI metadata: {'ai_metadata' in first_component}")
            
            # Check categories
            categories = set()
            for comp in components:
                if 'actionGroup' in comp:
                    categories.add(comp['actionGroup'])
            
            print(f"[INFO] Categories found: {len(categories)}")
            print(f"[INFO] Categories: {', '.join(sorted(categories))}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return 1

if __name__ == "__main__":
    exit(test_components_file())