#!/usr/bin/env python3
"""
Test Script for Kokoro TTS API
This script tests the Kokoro text-to-speech API running on localhost:8880
"""

import requests
import json
import base64
import time
import os
from typing import Optional

class KokoroAPITester:
    def __init__(self, base_url: str = "http://localhost:8880/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def test_connection(self) -> bool:
        """Test if the Kokoro API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"✓ Connection test: Status {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection test failed: {e}")
            return False

    def get_available_voices(self) -> Optional[dict]:
        """Get list of available voices"""
        try:
            response = self.session.get(f"{self.base_url}/voices")
            if response.status_code == 200:
                voices = response.json()
                print("✓ Available voices:", voices)
                return voices
            else:
                print(f"✗ Failed to get voices: Status {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting voices: {e}")
            return None

    def synthesize_speech(self, text: str, voice: str = "default",
                         output_file: str = "output.wav") -> bool:
        """Convert text to speech using Kokoro API"""

        url = f"{self.base_url}/tts"

        # Request payload
        payload = {
            "text": text,
            "voice": voice,
            "format": "wav"
        }

        try:
            print(f"🎵 Synthesizing: '{text}' with voice '{voice}'")
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                # Save audio file
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"✓ Audio saved to: {output_file}")
                print(f"  File size: {len(response.content)} bytes")
                return True
            else:
                print(f"✗ TTS request failed: Status {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Error during TTS request: {e}")
            return False

    def test_with_base64(self, text: str, voice: str = "default") -> Optional[str]:
        """Test TTS with base64 encoded audio response"""

        url = f"{self.base_url}/tts"

        payload = {
            "text": text,
            "voice": voice,
            "format": "wav",
            "return_base64": True
        }

        try:
            print(f"🎵 Testing base64 TTS: '{text}'")
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                result = response.json()
                if "audio" in result:
                    audio_data = result["audio"]
                    print(f"✓ Base64 audio received (length: {len(audio_data)} chars)")

                    # Decode and save for verification
                    audio_bytes = base64.b64decode(audio_data)
                    with open("output_base64.wav", "wb") as f:
                        f.write(audio_bytes)
                    print("✓ Base64 audio saved to: output_base64.wav")
                    return audio_data
                else:
                    print("✗ No audio data in response")
                    return None
            else:
                print(f"✗ Base64 TTS request failed: Status {response.status_code}")
                print(f"  Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"✗ Error during base64 TTS request: {e}")
            return None

    def run_comprehensive_test(self):
        """Run a comprehensive test of the Kokoro API"""
        print("🚀 Starting Kokoro API Test Suite")
        print("=" * 50)

        # Test 1: Connection
        print("\n1. Testing API connection...")
        if not self.test_connection():
            print("❌ Cannot connect to Kokoro API. Make sure the container is running.")
            return False

        # Test 2: Get voices
        print("\n2. Getting available voices...")
        voices = self.get_available_voices()
        if not voices:
            print("⚠️  Could not get voices, continuing with default voice...")

        # Test 3: Basic TTS
        print("\n3. Testing basic text-to-speech...")
        test_texts = [
            "Hello, this is a test of the Kokoro text-to-speech system.",
            "Welcome to the voice assistant application.",
            "This is a demonstration of the TTS capabilities."
        ]

        for i, text in enumerate(test_texts, 1):
            output_file = f"test_output_{i}.wav"
            success = self.synthesize_speech(text, voice="default", output_file=output_file)
            if success:
                print(f"  ✓ Test {i} passed")
            else:
                print(f"  ❌ Test {i} failed")
            time.sleep(1)  # Small delay between requests

        # Test 4: Base64 TTS
        print("\n4. Testing base64 audio response...")
        base64_result = self.test_with_base64("This is a base64 audio test.")
        if base64_result:
            print("  ✓ Base64 test passed")
        else:
            print("  ❌ Base64 test failed")

        # Test 5: Different voices (if available)
        if voices and isinstance(voices, dict):
            print("\n5. Testing different voices...")
            for voice_name in voices.keys():
                if voice_name != "default":
                    output_file = f"test_voice_{voice_name}.wav"
                    success = self.synthesize_speech(
                        f"This is a test of the {voice_name} voice.",
                        voice=voice_name,
                        output_file=output_file
                    )
                    if success:
                        print(f"  ✓ Voice '{voice_name}' test passed")
                    else:
                        print(f"  ❌ Voice '{voice_name}' test failed")
                    time.sleep(1)

        print("\n" + "=" * 50)
        print("🎉 Kokoro API Test Suite Complete!")
        print("📁 Check the generated audio files in the current directory.")

        return True

def main():
    """Main function to run the test"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Kokoro TTS API")
    parser.add_argument("--url", default="http://localhost:8880/v1",
                       help="Kokoro API base URL (default: http://localhost:8880/v1)")
    parser.add_argument("--text", default="Hello, this is a test of the Kokoro text-to-speech system.",
                       help="Text to convert to speech")
    parser.add_argument("--voice", default="af_alloy", help="Voice to use")
    parser.add_argument("--output", default="test_output.wav", help="Output audio file")
    parser.add_argument("--base64", action="store_true", help="Test base64 response")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test suite")

    args = parser.parse_args()

    # Initialize tester
    tester = KokoroAPITester(args.url)

    if args.comprehensive:
        # Run comprehensive test suite
        tester.run_comprehensive_test()
    else:
        # Run single test
        if args.base64:
            tester.test_with_base64(args.text, args.voice)
        else:
            tester.synthesize_speech(args.text, args.voice, args.output)

if __name__ == "__main__":
    main()