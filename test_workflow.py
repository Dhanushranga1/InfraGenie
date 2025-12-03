#!/usr/bin/env python3
"""
Test script to verify InfraGenie workflow with dual-model optimization
This script sends a test request and monitors the response
"""

import requests
import json
import time

# Test configuration
API_URL = "http://localhost:8000"
TEST_PROMPT = "create a simple EC2 instance with nginx and a security group allowing HTTP traffic"

def test_workflow():
    print("🧪 Testing InfraGenie Workflow")
    print("=" * 60)
    print(f"📝 Test Prompt: {TEST_PROMPT}")
    print("=" * 60)
    
    # Send request
    print("\n📤 Sending request to backend...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/generate",
            json={"prompt": TEST_PROMPT},
            timeout=600  # 10 minute timeout
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ Response received in {duration:.2f} seconds")
        print("=" * 60)
        
        # Parse response
        if response.status_code == 200:
            data = response.json()
            
            # Check results
            print("\n📊 Response Analysis:")
            print(f"  - Has Terraform code: {'✅' if data.get('terraform_code') else '❌'}")
            print(f"  - Has Ansible playbook: {'✅' if data.get('ansible_playbook') else '❌'}")
            print(f"  - Has graph data: {'✅' if data.get('graph_data') else '❌'}")
            
            if data.get('terraform_code'):
                tf_length = len(data['terraform_code'])
                print(f"  - Terraform code length: {tf_length} chars")
            
            if data.get('graph_data'):
                nodes = len(data['graph_data'].get('nodes', []))
                edges = len(data['graph_data'].get('edges', []))
                print(f"  - Graph nodes: {nodes}")
                print(f"  - Graph edges: {edges}")
            
            if data.get('validation_error'):
                print(f"\n⚠️  Validation error: {data['validation_error']}")
            
            # Show workflow stages
            if data.get('workflow_stage'):
                print(f"\n  - Final stage: {data['workflow_stage']}")
            
            print("\n" + "=" * 60)
            print("✅ Workflow test completed successfully!")
            print("=" * 60)
            
            # Check if download button should be enabled
            has_content = bool(data.get('terraform_code'))
            print(f"\n🔽 Download button should be: {'✅ ENABLED' if has_content else '❌ DISABLED'}")
            print(f"🎨 Architecture diagram should: {'✅ RENDER' if data.get('graph_data') else '❌ BE EMPTY'}")
            
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 429:
                print("\n⚠️  Rate limit exceeded!")
                print("Solutions:")
                print("  1. Wait for rate limit to reset")
                print("  2. Add GROQ_API_KEY_SECONDARY to .env")
                print("  3. Upgrade Groq tier")
    
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (>10 minutes)")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to backend")
        print("Is the backend running on http://localhost:8000?")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 InfraGenie Workflow Test")
    print("This will test the dual-model optimization system\n")
    
    # Check if backend is running
    try:
        health = requests.get(f"{API_URL}/", timeout=5)
        print("✅ Backend is running\n")
    except:
        print("❌ Backend is not responding")
        print("Please start the backend first: bash backend/start.sh\n")
        exit(1)
    
    test_workflow()
