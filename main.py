import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module
import time
import os

def read_api_key(file_path: str) -> None:
    """Read API key from a file and set it as an environment variable."""
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    os.environ['OPENAI_API_KEY'] = line.strip().split('=')[1]
                    print("API key read successfully")
                    return
        print("Error: OPENAI_API_KEY not found in the file")
    except FileNotFoundError:
        print(f"Error: API key file '{file_path}' not found")

def read_prompts(file_path: str) -> Dict[str, str]:
    """Read prompts from a file and return as a dictionary."""
    prompts = {}
    try:
        with open(file_path, 'r') as f:
            current_module = None
            current_prompt = []
            for line in f:
                if line.startswith('[') and line.endswith(']\n'):
                    if current_module:
                        prompts[current_module] = ''.join(current_prompt).strip()
                    current_module = line.strip()[1:-1]
                    current_prompt = []
                else:
                    current_prompt.append(line)
            if current_module:
                prompts[current_module] = ''.join(current_prompt).strip()
        print(f"Prompts read: {list(prompts.keys())}")
        return prompts
    except FileNotFoundError:
        print(f"Error: Prompt file '{file_path}' not found")
        return {}

class GlobalWorkspace:
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.last_output = None
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def process(self, module_outputs: Dict[str, str]) -> str:
        """Process module outputs and return a timestamped response."""
        formatted_outputs = "\n".join([f"{module}: {output}" for module, output in module_outputs.items()])
        input_data = f"{self.prompt}\n\nModule Outputs:\n{formatted_outputs}"
        
        try:
            response = await self._make_api_call(input_data)
            timestamp = datetime.now().isoformat()
            self.last_output = f"[{timestamp}] {response}"
            return self.last_output
        except Exception as e:
            response = f"Error: An unexpected error occurred: {str(e)}"
            timestamp = datetime.now().isoformat()
            self.last_output = f"[{timestamp}] {response}"
            return self.last_output

    async def _make_api_call(self, input_data: str) -> str:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": input_data}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result['choices'][0]['message']['content']

    def broadcast(self) -> str:
        """Return the most recent Global Workspace output."""
        return self.last_output

def print_loading_bar(progress):
    bar_length = 20
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\rThinking: [{bar}] {progress*100:.0f}%', end='', flush=True)

async def main():
    # Read API key and prompts
    read_api_key('api_keys.txt')
    prompts = read_prompts('prompts.txt')

    print(f"Prompts: {list(prompts.keys())}")

    # Initialize modules
    try:
        modules = {
            'PIM': Module('PIM', prompts['PIM']),
            'RAM': Module('RAM', prompts['RAM']),
            'EM': Module('EM', prompts['EM']),
            'CSM': Module('CSM', prompts['CSM']),
            'ECM': Module('ECM', prompts['ECM']),
            'RGM': Module('RGM', prompts['RGM']),
        }
    except KeyError as e:
        print(f"Error: Missing key {e} in prompts")
        return

    # Initialize Global Workspace
    gw = GlobalWorkspace(prompts['GW'])

    while True:
        # User Input Reception
        user_input = input("\nEnter your input (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break

        print("\nAda is thinking...")
        
        # Update PIM with user input
        print_loading_bar(0.1)
        pim_output = await modules['PIM'].process(user_input)

        continue_thinking = True
        thinking_steps = 0
        while continue_thinking:
            thinking_steps += 1
            # Cognitive Processing
            module_outputs = {}
    
            # Process PIM and all other cognitive modules except ECM
            modules_to_process = ['PIM', 'RAM', 'EM', 'CSM']

            for module_name in modules_to_process:
                if module_name == 'PIM' and module_name in module_outputs:
                    continue  # Skip PIM if it's already processed
                module_outputs[module_name] = await modules[module_name].process(user_input)

            print_loading_bar(0.1 + 0.3 * thinking_steps / 5)  # Progress the loading bar

            # Global Workspace Processing
            gw_output = await gw.process(module_outputs)

            # Broadcast GW output
            broadcast = gw.broadcast()

            print_loading_bar(0.1 + 0.3 * thinking_steps / 5 + 0.1)  # Progress the loading bar

            # ECM processes after all other modules
            ecm_output = await modules['ECM'].process(broadcast)
            module_outputs['ECM'] = ecm_output

            # ECM decides whether to continue thinking or generate response
            continue_thinking = 'continue' in ecm_output.lower()

            if thinking_steps >= 4:  # Limit the number of thinking cycles to 4
                continue_thinking = False

            print_loading_bar(0.1 + 0.3 * thinking_steps / 5 + 0.2)  # Progress the loading bar

        # Response Generation
        print_loading_bar(0.9)
        response = await modules['RGM'].process(broadcast)
        print_loading_bar(1)
        print("\n\nAda's response:")
        print(response)
        print("\n" + "-"*50)  # Add a separator line

if __name__ == "__main__":
    asyncio.run(main())
