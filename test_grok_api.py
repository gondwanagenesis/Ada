import requests
import json

def test_grok_api():
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY_HERE",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    print("API Call Details:")
    print(f"  URL: {url}")
    print(f"  Headers: {headers}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        json_response = response.json()
        print("API Response:")
        print(json.dumps(json_response, indent=2))
        if 'error' in json_response:
            print(f"Error from API: {json_response['error']}")
        elif 'choices' in json_response and len(json_response['choices']) > 0:
            print("Generated response:")
            print(json_response['choices'][0]['message']['content'].strip())
        else:
            print("Unexpected response format")
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {str(e)}")

if __name__ == "__main__":
    test_grok_api()
