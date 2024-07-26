from typing import Any
import aiohttp
import json
import asyncio
from typing import Any
import os

class Module:
    def __init__(self, name: str, prompt: str, api_key: str):
        self.name = name
        self.prompt = prompt
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def process(self, input_data: Any) -> str:
        """
        Process input data using the module's prompt and API key.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            str: The processed output.
        """
        try:
            return await self._make_api_call(input_data)
        except Exception as e:
            return f"Error: An unexpected error occurred: {str(e)}"

    async def _make_api_call(self, input_data: Any) -> str:
        full_input = f"{self.prompt}\n\nInput: {input_data}"
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": full_input}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result['choices'][0]['message']['content']

class GroqModule(Module):
    def __init__(self, name: str, prompt: str, api_key: str):
        super().__init__(name, prompt, api_key)
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def _make_api_call(self, input_data: Any) -> str:
        full_input = f"{self.prompt}\n\nInput: {input_data}"
        
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": full_input}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result['choices'][0]['message']['content']
