import requests
import json

# Load API keys from the text file
def load_api_keys(file_path='apikeys.txt'):
    api_keys = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            current_module = None
            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):  # Module name
                    current_module = line[1:-1]
                elif current_module:
                    api_keys[current_module] = line
        print(f"Loaded API keys for modules: {', '.join(api_keys.keys())}")
    except FileNotFoundError:
        print("Error: API keys file not found!")
    except Exception as e:
        print(f"Error loading API keys: {str(e)}")
    return api_keys

# Test API call for a specific module
def test_api_call(module, api_key, prompt="Hello, world!"):
    url = "https://api.x.ai/v1/chat/completions"  # Adjust if needed
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-beta",  # Adjust if a different model is required
        "messages": [
            {"role": "system", "content": f"System prompt for {module}"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    print(f"\nTesting module: {module}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for bad status codes
        json_response = response.json()
        print(f"Response for {module}: {json.dumps(json_response, indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"API call failed for {module}: {e}")
    except Exception as e:
        print(f"Unexpected error for {module}: {e}")

# Main function to test all modules
def main():
    api_keys = load_api_keys()  # Load API keys from text file

    if not api_keys:
        print("No API keys found. Exiting.")
        return

    for module, api_key in api_keys.items():
        test_api_call(module, api_key)

if __name__ == "__main__":
    main()
