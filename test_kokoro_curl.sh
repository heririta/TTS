#!/bin/bash

# Kokoro API Test Script using curl
# This script tests the Kokoro TTS API endpoints

KOKORO_URL="http://localhost:8880/v1"
OUTPUT_DIR="./kokoro_test_outputs"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "🚀 Testing Kokoro TTS API"
echo "API URL: $KOKORO_URL"
echo "Output directory: $OUTPUT_DIR"
echo "================================"

# Function to test API endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=$3
    local description=$4

    echo ""
    echo "📍 Testing: $description"
    echo "Endpoint: $method $endpoint"

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
            -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$KOKORO_URL$endpoint")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
            -X GET \
            "$KOKORO_URL$endpoint")
    fi

    # Extract HTTP status and response body
    http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
    body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

    if [ "$http_code" = "200" ]; then
        echo "✅ Success (HTTP $http_code)"
        echo "Response: $body"
    else
        echo "❌ Failed (HTTP $http_code)"
        echo "Response: $body"
    fi
}

# Function to test TTS synthesis
test_tts() {
    local text=$1
    local voice=${2:-default}
    local output_file=$3
    local description=$4

    echo ""
    echo "🎵 Testing: $description"
    echo "Text: '$text'"
    echo "Voice: $voice"
    echo "Output: $output_file"

    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"$text\",\"voice\":\"$voice\",\"format\":\"wav\"}" \
        "$KOKORO_URL/tts")

    http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
    body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

    if [ "$http_code" = "200" ]; then
        # Save audio data to file
        echo "$body" > "$output_file"
        file_size=$(wc -c < "$output_file")
        echo "✅ Success (HTTP $http_code)"
        echo "Audio saved: $output_file ($file_size bytes)"
    else
        echo "❌ Failed (HTTP $http_code)"
        echo "Response: $body"
    fi
}

# Function to test TTS with base64 response
test_tts_base64() {
    local text=$1
    local voice=${2:-default}
    local description=$3

    echo ""
    echo "🎵 Testing: $description"
    echo "Text: '$text'"
    echo "Voice: $voice"
    echo "Format: Base64 encoded audio"

    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"$text\",\"voice\":\"$voice\",\"format\":\"wav\",\"return_base64\":true}" \
        "$KOKORO_URL/tts")

    http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
    body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

    if [ "$http_code" = "200" ]; then
        # Try to parse JSON and extract audio field
        audio_data=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'audio' in data:
        print(data['audio'])
    else:
        print('No audio field in response')
except:
    print('Invalid JSON response')
" 2>/dev/null)

        if [ "$audio_data" != "No audio field in response" ] && [ "$audio_data" != "Invalid JSON response" ]; then
            echo "✅ Success (HTTP $http_code)"
            echo "Base64 audio received (length: $(echo -n "$audio_data" | wc -c) chars)"

            # Optionally decode and save
            if command -v base64 >/dev/null 2>&1; then
                echo "$audio_data" | base64 -d > "$OUTPUT_DIR/test_base64_output.wav"
                echo "Decoded audio saved: $OUTPUT_DIR/test_base64_output.wav"
            fi
        else
            echo "❌ Invalid response format"
            echo "Response: $body"
        fi
    else
        echo "❌ Failed (HTTP $http_code)"
        echo "Response: $body"
    fi
}

# Test 1: Basic connectivity
test_endpoint "" "GET" "" "Basic connectivity test"

# Test 2: Get available voices
test_endpoint "/voices" "GET" "" "Get available voices"

# Test 3: Basic TTS test
test_tts "Hello, this is a test of the Kokoro text-to-speech system." "default" "$OUTPUT_DIR/test_basic.wav" "Basic TTS synthesis"

# Test 4: TTS with different text
test_tts "Welcome to the voice assistant application. This is working perfectly." "default" "$OUTPUT_DIR/test_welcome.wav" "Welcome message TTS"

# Test 5: TTS with longer text
test_tts "The quick brown fox jumps over the lazy dog. This pangram sentence contains all letters of the alphabet and is commonly used for testing font rendering and text-to-speech systems." "default" "$OUTPUT_DIR/test_long.wav" "Longer text TTS"

# Test 6: Base64 TTS test
test_tts_base64 "This is a test of base64 encoded audio response from the Kokoro TTS system." "default" "Base64 audio test"

# Test 7: Test with different voice (if available)
test_tts "Testing with a different voice option." "af_sarah" "$OUTPUT_DIR/test_sarah.wav" "Alternative voice test (af_sarah)"

echo ""
echo "================================"
echo "🎉 Kokoro API Test Complete!"
echo "📁 Check the output directory: $OUTPUT_DIR"
echo ""
echo "Generated files:"
ls -la "$OUTPUT_DIR" 2>/dev/null || echo "No files generated"

# Instructions for playing audio files
echo ""
echo "🎧 To play the generated audio files:"
echo "   - On macOS/Linux: afplay <file> or aplay <file>"
echo "   - On Windows: Start-Process <file> in PowerShell or double-click"
echo "   - Or use any audio player: VLC, Windows Media Player, etc."