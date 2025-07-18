#!/usr/bin/env python3
"""
Test script for HuggingFace model integration
Tests the complete pipeline from HF repo to audio generation
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def check_docker():
    """Check if Docker and Docker Compose are available"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker", "compose", "version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose not found. Please install them first.")
        return False

def create_test_env():
    """Create a test .env file"""
    env_content = """# Test configuration for HuggingFace model
ORPHEUS_API_URL=http://llama-cpp-server:5006/v1/completions
ORPHEUS_HF_REPO=dr-flex/orpheus-lena
ORPHEUS_MODEL_TYPE=fp16
ORPHEUS_MAX_TOKENS=8192
ORPHEUS_TEMPERATURE=0.6
ORPHEUS_TOP_P=0.9
ORPHEUS_SAMPLE_RATE=24000
ORPHEUS_PORT=5005
ORPHEUS_HOST=0.0.0.0
ORPHEUS_API_TIMEOUT=120

# Performance settings for 16-bit models
LLAMA_THREADS=8
LLAMA_BATCH_SIZE=32768
LLAMA_UBATCH_SIZE=16384
LLAMA_CTX_SIZE=49152
LLAMA_PARALLEL=4
LLAMA_THREADS_HTTP=4
"""
    
    if Path(".env").exists():
        backup_name = f".env.backup.{int(time.time())}"
        print(f"📦 Backing up existing .env to {backup_name}")
        Path(".env").rename(backup_name)
    
    Path(".env").write_text(env_content)
    print("✅ Created test .env file")

def start_services():
    """Start Docker services"""
    print("\n🚀 Starting services with HuggingFace model conversion...")
    print("This may take several minutes on first run to download and convert the model.")
    
    cmd = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.hf.yml", "up", "--build", "-d"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to start services:\n{result.stderr}")
        return False
    
    print("✅ Services started successfully")
    return True

def wait_for_server(max_wait=300):
    """Wait for the server to be ready"""
    print("\n⏳ Waiting for server to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:5005/docs")
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        print(f"   Waiting... ({elapsed}s elapsed)")
    
    print("❌ Server failed to start within timeout")
    return False

def test_tts_generation():
    """Test TTS generation"""
    print("\n🎤 Testing TTS generation...")
    
    test_data = {
        "model": "orpheus",
        "input": "Hello! This is a test of the Orpheus text-to-speech system using a HuggingFace model. <laugh> It's working great!",
        "voice": "tara",
        "response_format": "wav",
        "speed": 1.0
    }
    
    try:
        response = requests.post(
            "http://localhost:5005/v1/audio/speech",
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            output_file = "test_output_hf.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"✅ Audio generated successfully! Saved to {output_file}")
            print(f"   File size: {len(response.content):,} bytes")
            return True
        else:
            print(f"❌ TTS generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during TTS generation: {e}")
        return False

def check_logs():
    """Display relevant logs"""
    print("\n📋 Checking conversion logs...")
    result = subprocess.run(
        ["docker", "logs", "model-converter", "--tail", "50"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print("Model Converter logs:")
        print(result.stdout)

def cleanup():
    """Stop services"""
    print("\n🧹 Stopping services...")
    subprocess.run(["docker", "compose", "down"], capture_output=True)
    print("✅ Services stopped")

def main():
    """Main test flow"""
    print("🧪 Orpheus HuggingFace Model Integration Test")
    print("=" * 50)
    
    if not check_docker():
        return 1
    
    try:
        create_test_env()
        
        if not start_services():
            check_logs()
            return 1
        
        if not wait_for_server():
            check_logs()
            return 1
        
        if test_tts_generation():
            print("\n✨ All tests passed! HuggingFace model integration is working.")
            return 0
        else:
            check_logs()
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    finally:
        cleanup()

if __name__ == "__main__":
    sys.exit(main())