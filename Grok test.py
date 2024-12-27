import asyncio
import aiohttp
import time
import logging
import re
from typing import Dict
from tqdm.asyncio import tqdm

# Configure Logging
logging.basicConfig(
    filename='grok_api_test.log',
    filemode='w',  # Overwrite the log file each run
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Your Grok API Key
API_KEY = "xai-TLFugtDWM1ByCeA0OnBn5jqRyUnXHTQCfQxRZ0GIJJNaCadrIkCqAdtZA6psrvAXCIVEBkQbZFYXln1d"

# API Endpoint (Assuming it's the same for all modules)
API_ENDPOINT = "https://api.x.ai/v1/chat/completions"

# Define Module Prompts
MODULE_PROMPTS = {
    "GW": "You are the Global Workspace module. Process the following information and prepare it for other modules.",
    "RM": "You are the Reasoning Module. Analyze the given input and provide logical insights.",
    "CM": "You are the Creative Module. Generate creative ideas based on the input.",
    "EC": "You are the Executive Control Module. Refine and integrate outputs from other modules.",
    "LM": "You are the Language Module. Generate a direct and natural response to the user without including any internal thoughts or module outputs."
}

# Function to Clean Module Output
def clean_output(output: str) -> str:
    """
    Cleans the module output by removing any prompts, system messages, or disallowed content.
    """
    output = re.sub(r'\[.*?\]', '', output)  # Remove text within brackets
    output = re.sub(r'(You are|Your role is|For each input:).*', '', output, flags=re.DOTALL)
    return output.strip()

# Asynchronous Function to Test a Single Module
async def test_module(session: aiohttp.ClientSession, module: str, prompt: str) -> Dict[str, float]:
    """
    Sends a request to the specified module and measures the response time.
    Returns a dictionary with module name and response duration.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "This is a test message to evaluate performance."}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "stop": ["[", "]", "You are", "Your role is"]
    }

    start_time = time.time()
    try:
        async with session.post(API_ENDPOINT, headers=headers, json=payload, timeout=30) as response:
            response.raise_for_status()
            json_response = await response.json()
            content = json_response.get('choices', [{}])[0].get('message', {}).get('content', '')
            duration = time.time() - start_time
            cleaned_content = clean_output(content)
            logging.info(f"Module: {module}, Duration: {duration:.4f} seconds, Response: {cleaned_content}")
            return {"module": module, "duration": duration}
    except Exception as e:
        duration = time.time() - start_time
        logging.error(f"Module: {module}, Duration: {duration:.4f} seconds, Error: {str(e)}")
        return {"module": module, "duration": duration, "error": str(e)}

# Main Asynchronous Function to Test All Modules
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for module, prompt in MODULE_PROMPTS.items():
            tasks.append(test_module(session, module, prompt))
        
        # Use tqdm for progress bar
        results = []
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Testing Modules"):
            result = await f
            results.append(result)
        
        # Display Results
        print("\n--- API Call Durations ---")
        for result in results:
            module = result.get("module")
            duration = result.get("duration")
            error = result.get("error", None)
            if error:
                print(f"{module}: ERROR - {error} (Duration: {duration:.2f} seconds)")
            else:
                print(f"{module}: {duration:.2f} seconds")
        
        # Total Time
        total_duration = sum([res.get("duration", 0) for res in results])
        print(f"\nTotal Processing Time: {total_duration:.2f} seconds")

# Run the Asynchronous Main Function
if __name__ == "__main__":
    asyncio.run(main())
