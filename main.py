import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module
import time
import configparser

def read_api_keys(file_path: str, api_type: str) -> Dict[str, str]:
    """Read API keys from a file and return as a dictionary."""
    config = configparser.ConfigParser()
    config.read(file_path)
    try:
        api_keys = dict(config[api_type])
        print(f"API keys read for {api_type}: {list(api_keys.keys())}")
        return api_keys
    except KeyError:
        print(f"Error: '{api_type}' section not found in {file_path}")
        print(f"Available sections: {config.sections()}")
        return {}

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

import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module

class GlobalWorkspace:
    def __init__(self, prompt: str, api_key: str, api_type: str):
        self.prompt = prompt
        self.api_key = api_key
        self.last_output = None
        self.api_type = api_type
        self.api_url = "https://api.groq.com/openai/v1/chat/completions" if api_type == 'GROQ' else "https://api.openai.com/v1/chat/completions"

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
            "model": "mixtral-8x7b-32768" if self.api_type == 'GROQ' else "gpt-4",
            "messages": [{"role": "user", "content": input_data}],
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

    def broadcast(self) -> str:
        """Return the most recent Global Workspace output."""
        return self.last_output

def print_loading_bar(progress):
    bar_length = 20
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\rThinking: [{bar}] {progress*100:.0f}%', end='', flush=True)

async def main():
    # Ask user which API to use
    while True:
        api_choice = input("Which API would you like to use? (1 for GPT4All, 2 for Groq): ").strip()
        if api_choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")

    api_type = 'OPENAI' if api_choice == '1' else 'GROQ'
    
    # Read API keys and prompts
    api_keys = read_api_keys('api_keys.txt', api_type)
    prompts = read_prompts('prompts.txt')

    print(f"API keys: {list(api_keys.keys())}")
    print(f"Prompts: {list(prompts.keys())}")

    # Initialize modules
    try:
        modules = {
            'PIM': Module('PIM', prompts['PIM'], api_keys['PIM'], api_type),
            'RAM': Module('RAM', prompts['RAM'], api_keys['RAM'], api_type),
            'EM': Module('EM', prompts['EM'], api_keys['EM'], api_type),
            'CSM': Module('CSM', prompts['CSM'], api_keys['CSM'], api_type),
            'ECM': Module('ECM', prompts['ECM'], api_keys['ECM'], api_type),
            'RGM': Module('RGM', prompts['RGM'], api_keys['RGM'], api_type),
        }
    except KeyError as e:
        print(f"Error: Missing key {e} in either api_keys or prompts")
        return

    # Initialize Global Workspace
    gw = GlobalWorkspace(prompts['GW'], api_keys['GW'], api_type)

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
