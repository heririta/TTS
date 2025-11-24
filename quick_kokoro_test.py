#!/usr/bin/env python3
"""
Quick Kokoro TTS API Test
Simple test that works on Windows
"""

import requests

def test_kokoro():
    base_url = "http://localhost:8880/v1"

    print("Testing Kokoro TTS API...")

    # Test data
    test_cases = [
        {"text": "Hello, this is a test with Sarah's voice.", "voice": "af_sarah", "output": "test_sarah.wav"},
        {"text": "Welcome to the voice assistant.", "voice": "af_bella", "output": "test_bella.wav"},
        {"text": "This is Michael speaking.", "voice": "am_michael", "output": "test_michael.wav"}
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['voice']}")
        print(f"Text: {test['text']}")

        try:
            response = requests.post(
                f"{base_url}/audio/speech",
                json={
                    "input": test["text"],
                    "voice": test["voice"],
                    "response_format": "wav"
                }
            )

            if response.status_code == 200:
                with open(test["output"], "wb") as f:
                    f.write(response.content)
                print(f"SUCCESS: Audio saved to {test['output']} ({len(response.content)} bytes)")
            else:
                print(f"FAILED: Status {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"ERROR: {e}")

    print("\nTest completed! Check the generated .wav files.")

if __name__ == "__main__":
    test_kokoro()