#!/usr/bin/env python3
"""
Kokoro TTS API Test Script for Windows
This script tests the Kokoro text-to-speech API running on localhost:8880
Windows-compatible version without Unicode characters
"""

import requests
import json
import base64
import time
import os
from typing import Optional

class KokoroAPITester:
    def __init__(self, base_url: str = "http://77.104.167.149:54605/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def test_connection(self) -> bool:
        """Test if the Kokoro API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"[+] Connection test: Status {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"[-] Connection test failed: {e}")
            return False

    def get_available_voices(self) -> Optional[dict]:
        """Get list of available voices"""
        try:
            response = self.session.get(f"{self.base_url}/audio/voices")
            if response.status_code == 200:
                voices = response.json()
                print("[+] Available voices:", voices)
                return voices
            else:
                print(f"[-] Failed to get voices: Status {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[-] Error getting voices: {e}")
            return None

    def synthesize_speech(self, text: str, voice: str = "default",
                         output_file: str = "output.wav") -> bool:
        """Convert text to speech using Kokoro API"""

        url = f"{self.base_url}/audio/speech"

        # Request payload
        payload = {
            "input": text,
            "voice": voice,
            "response_format": "wav"
        }

        try:
            print(f"[*] Synthesizing: '{text}' with voice '{voice}'")
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                # Save audio file
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"[+] Audio saved to: {output_file}")
                print(f"    File size: {len(response.content)} bytes")
                return True
            else:
                print(f"[-] TTS request failed: Status {response.status_code}")
                print(f"    Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"[-] Error during TTS request: {e}")
            return False

    def run_simple_test(self):
        """Run a simple test of the Kokoro API"""
        print("Starting Kokoro API Test")
        print("=" * 40)

        # Test 1: Connection
        print("\n1. Testing API connection...")
        if not self.test_connection():
            print("[-] Cannot connect to Kokoro API. Make sure the container is running.")
            return False

        # Test 2: Get voices
        print("\n2. Getting available voices...")
        voices = self.get_available_voices()
        if not voices:
            print("[!] Could not get voices, continuing with default voice...")

        # Test 3: Basic TTS
        print("\n3. Testing basic text-to-speech...")
        test_texts = [
            "Hello, this is a test of the Kokoro text-to-speech system.",
            "Welcome to the voice assistant application.",
            "This is a demonstration of the TTS capabilities."
        ]

        for i, text in enumerate(test_texts, 1):
            output_file = f"test_output_{i}.wav"
            success = self.synthesize_speech(text, voice="af_sarah", output_file=output_file)
            if success:
                print(f"    [+] Test {i} passed")
            else:
                print(f"    [-] Test {i} failed")
            time.sleep(1)  # Small delay between requests

        print("\n" + "=" * 40)
        print("[+] Kokoro API Test Complete!")
        print("[*] Check the generated audio files in the current directory.")

        return True

def main():
    """Main function to run the test"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Kokoro TTS API")
    parser.add_argument("--url", default="http://77.104.167.149:54605/v1",
                       help="Kokoro API base URL (default: http://77.104.167.149:54605/v1)")
    parser.add_argument("--text", default="Hello, this is a test of the Kokoro text-to-speech system.",
                       help="Text to convert to speech")
    parser.add_argument("--voice", default="af_sarah", help="Voice to use")
    parser.add_argument("--output", default="test_output.wav", help="Output audio file")
    parser.add_argument("--simple", action="store_true", help="Run simple test suite")

    args = parser.parse_args()

    # Initialize tester
    tester = KokoroAPITester(args.url)

    if args.simple:
        # Run simple test suite
        tester.run_simple_test()
    else:
        # Run single test
        tester.synthesize_speech(args.text, args.voice, args.output)

if __name__ == "__main__":
    main()