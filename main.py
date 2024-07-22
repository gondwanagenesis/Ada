import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module
import time

def read_api_keys(file_path: str) -> Dict[str, str]:
    """Read API keys from a file and return as a dictionary."""
    api_keys = {}
    with open(file_path, 'r') as f:
        for line in f:
            module_name, api_key = line.strip().split('=')
            api_keys[module_name] = api_key
    return api_keys

def read_prompts(file_path: str) -> Dict[str, str]:
    """Read prompts from a file and return as a dictionary."""
    prompts = {}
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
    return prompts

import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module

class GlobalWorkspace:
    def __init__(self, prompt: str, api_key: str):
        self.prompt = prompt
        self.api_key = api_key
        self.last_output = None
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def process(self, module_outputs: Dict[str, str]) -> str:
        """Process module outputs and return a timestamped response."""
        formatted_outputs = "\n".join([f"{module}: {output}" for module, output in module_outputs.items()])
        input_data = f"{self.prompt}\n\nModule Outputs:\n{formatted_outputs}"
        
        max_retries = 3
        retry_delay = 5  # seconds
        backoff_factor = 2  # Exponential backoff factor

        for attempt in range(max_retries):
            try:
                response = await self._make_api_call(input_data)
                timestamp = datetime.now().isoformat()
                self.last_output = f"[{timestamp}] {response}"
                return self.last_output
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (backoff_factor ** attempt)
                        print(f"Global Workspace: Rate limit exceeded. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        response = f"Error: Rate limit exceeded after {max_retries} attempts."
                else:
                    response = f"Error: Unable to process. Status code: {e.status}"
            except Exception as e:
                response = f"Error: An unexpected error occurred: {str(e)}"

        timestamp = datetime.now().isoformat()
        self.last_output = f"[{timestamp}] {response}"
        return self.last_output

    async def _make_api_call(self, input_data: str) -> str:
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": input_data}],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload)
            ) as response:
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
    # Read API keys and prompts
    api_keys = read_api_keys('api_keys.txt')
    prompts = read_prompts('prompts.txt')

    # Initialize modules
    modules = {
        'PIM': Module('PIM', prompts['PIM'], api_keys['PIM']),
        'RAM': Module('RAM', prompts['RAM'], api_keys['RAM']),
        'EM': Module('EM', prompts['EM'], api_keys['EM']),
        'CSM': Module('CSM', prompts['CSM'], api_keys['CSM']),
        'ECM': Module('ECM', prompts['ECM'], api_keys['ECM']),
        'RGM': Module('RGM', prompts['RGM'], api_keys['RGM']),
    }

    # Initialize Global Workspace
    gw = GlobalWorkspace(prompts['GW'], api_keys['GW'])

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
            tasks = []
            for module_name in ['PIM', 'RAM', 'EM', 'CSM', 'ECM']:
                if module_name == 'PIM' and module_name in module_outputs:
                    continue  # Skip PIM if it's already processed
                task = asyncio.create_task(modules[module_name].process(user_input))
                tasks.append(task)

            # Wait for all tasks to complete
            outputs = await asyncio.gather(*tasks)
            for module_name, output in zip(['PIM', 'RAM', 'EM', 'CSM', 'ECM'], outputs):
                module_outputs[module_name] = output

            print_loading_bar(0.1 + 0.3 * thinking_steps / 5)  # Progress the loading bar

            # Global Workspace Processing
            gw_output = await gw.process(module_outputs)

            # Broadcast GW output
            broadcast = gw.broadcast()

            print_loading_bar(0.1 + 0.3 * thinking_steps / 5 + 0.1)  # Progress the loading bar

            # ECM decides whether to continue thinking or generate response
            ecm_decision = await modules['ECM'].process(broadcast)
            continue_thinking = 'continue' in ecm_decision.lower()

            if thinking_steps >= 2:  # Limit the number of thinking cycles to 2
                continue_thinking = False

        # Response Generation
        print_loading_bar(0.9)
        response = await modules['RGM'].process(broadcast)
        print_loading_bar(1)
        print("\n\nAda's response:")
        print(response)
        print("\n" + "-"*50)  # Add a separator line

if __name__ == "__main__":
    asyncio.run(main())
