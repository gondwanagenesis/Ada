from typing import Any
import aiohttp
import json

class Module:
    def __init__(self, name: str, prompt: str, api_key: str):
        self.name = name
        self.prompt = prompt
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def process(self, input_data: Any) -> str:
        """
        Process input data using the module's prompt and API key.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            str: The processed output.
        """
        # Prepend module's prompt to input_data
        full_input = f"{self.prompt}\n\nInput: {input_data}"
        
        # Prepare the request payload
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": full_input}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Make the API call
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    output = result['choices'][0]['message']['content']
                else:
                    output = f"Error: Unable to process. Status code: {response.status}"

        return output
