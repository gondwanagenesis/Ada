import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module, GroqModule
import time
import os
import tkinter as tk
from tkinter import scrolledtext
import threading

# Configuration
MAX_THOUGHT_LOOPS = 1  # Easily changeable variable for the number of thought loops

def read_api_keys(file_path: str) -> Dict[str, str]:
    """Read API keys from a file and return as a dictionary."""
    api_keys = {}
    try:
        with open(file_path, 'r') as f:
            groq_section = False
            for line in f:
                line = line.strip()
                if line == "GROQ KEYS:":
                    groq_section = True
                elif '=' in line:
                    key, value = line.split('=', 1)
                    if groq_section:
                        module_name = key.split('_')[0]  # Extract module name (e.g., 'LM' from 'LM_API_KEY')
                        api_keys[module_name] = value.strip()
                    else:
                        api_keys[key] = value.strip()
        print("API keys read successfully")
        print(f"API keys found: {list(api_keys.keys())}")
        return api_keys
    except FileNotFoundError:
        print(f"Error: API key file '{file_path}' not found")
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
        if 'LM' not in prompts:
            print("Warning: 'LM' prompt not found. Please check your prompts.txt file.")
        return prompts
    except FileNotFoundError:
        print(f"Error: Prompt file '{file_path}' not found")
        return {}

class GlobalWorkspace:
    def __init__(self, prompt: str, api_key: str):
        self.prompt = prompt
        self.last_output = None
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.last_two_lm_responses = []

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
            "model": "gpt-3.5-turbo-1106",
            "messages": [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": input_data}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"API request failed with status {response.status}: {error_text}")
                result = await response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    raise ValueError(f"Unexpected API response: {result}")

    def broadcast(self) -> str:
        """Return the most recent Global Workspace output."""
        return self.last_output

    def update_lm_responses(self, response: str):
        """Update the last two LM responses."""
        self.last_two_lm_responses.append(response)
        if len(self.last_two_lm_responses) > 2:
            self.last_two_lm_responses.pop(0)

DEBUG_MODE = False
debug_window = None
debug_text = None

def print_loading_bar(progress):
    bar_length = 20
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\rThinking: [{bar}] {progress*100:.1f}%', end='', flush=True)

def create_debug_window():
    global debug_window, debug_text
    debug_window = tk.Tk()
    debug_window.title("Debug Output")
    debug_text = scrolledtext.ScrolledText(debug_window, wrap=tk.WORD)
    debug_text.pack(expand=True, fill='both')

def update_debug_window(message):
    if debug_text:
        debug_text.insert(tk.END, message + "\n")
        debug_text.see(tk.END)
        debug_window.update()

async def main():
    global DEBUG_MODE
    # Ask user if they want to run in debug mode
    debug_input = input("Do you want to run in debug mode? (y/n): ").lower()
    DEBUG_MODE = debug_input == 'y'

    if DEBUG_MODE:
        create_debug_window()

    # Read API keys and prompts
    api_keys = read_api_keys('api_keys.txt')
    prompts = read_prompts('prompts.txt')

    if DEBUG_MODE:
        update_debug_window(f"Prompts: {list(prompts.keys())}")
        update_debug_window(f"API keys: {list(api_keys.keys())}")
        debug_window.update()

    # Initialize modules
    try:
        modules = {
            'LM': Module('LM', prompts['LM'], api_keys['LM_API_KEY']),
            'ECM': Module('ECM', prompts['ECM'], api_keys['ECM_API_KEY']),
            'EM': GroqModule('EM', prompts['EM'], api_keys['EM']),
            'CM': GroqModule('CM', prompts['CM'], api_keys['CM']),
            'RM': GroqModule('RM', prompts['RM'], api_keys['RM']),
        }
        print("Modules initialized:")
        print("OpenAI API modules: LM, ECM")
        print("Groq API modules: EM, CM, RM")
    except KeyError as e:
        print(f"Error: Missing key {e} in prompts or API keys")
        return

    # Initialize Global Workspace
    gw = GlobalWorkspace(prompts['GW'], api_keys['GW_API_KEY'])
    print("Global Workspace initialized with OpenAI API")

    while True:
        # User Input Reception
        user_input = input("\nEnter your input (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break

        print("\nAda is thinking...")
        
        # Step 1: Send user input to LM
        print_loading_bar(0.1)
        lm_output = await modules['LM'].process(user_input)
        if DEBUG_MODE:
            update_debug_window(f"LM Output: {lm_output}")

        # Step 2: LM sends result to GW
        print_loading_bar(0.2)
        gw_output = await gw.process({'LM': lm_output})
        if DEBUG_MODE:
            update_debug_window(f"GW Output: {gw_output}")

        # Step 3: GW broadcasts to EM, CM, and RM
        print_loading_bar(0.3)
        broadcast = gw.broadcast()
        cognitive_modules = ['EM', 'CM', 'RM']
        cognitive_outputs = {}
        for i, module_name in enumerate(cognitive_modules):
            cognitive_outputs[module_name] = await modules[module_name].process(broadcast)
            print_loading_bar(0.3 + 0.1 * (i + 1) / len(cognitive_modules))
            if DEBUG_MODE:
                update_debug_window(f"{module_name} Output: {cognitive_outputs[module_name]}")

        # Step 4: Cognitive Modules send replies to GW
        print_loading_bar(0.6)
        gw_output = await gw.process(cognitive_outputs)
        if DEBUG_MODE:
            update_debug_window(f"GW Output after cognitive processing: {gw_output}")

        # Step 5: GW outputs to ECM
        print_loading_bar(0.7)
        ecm_output = await modules['ECM'].process(gw_output)
        if DEBUG_MODE:
            update_debug_window(f"ECM Output: {ecm_output}")

        # Step 6: ECM sends response to LM
        print_loading_bar(0.8)
        lm_final_input = f"User Input: {user_input}\n\nGlobal Workspace Output: {gw_output}\n\nECM Output: {ecm_output}"
        lm_final_output = await modules['LM'].process(lm_final_input)
        print_loading_bar(0.9)
        if DEBUG_MODE:
            update_debug_window(f"LM Final Input: {lm_final_input}")
            update_debug_window(f"LM Final Output: {lm_final_output}")

        # Step 7: LM gives final response and updates GW Dictionary
        ada_response = lm_final_output.split("Ada's response:", 1)[-1].strip()
        gw.update_lm_responses(ada_response)
        
        print("\n\nAda's response:")
        print(ada_response)
        
        # Log the response for debugging
        with open('response_log.txt', 'a') as log_file:
            log_file.write(f"Timestamp: {datetime.now().isoformat()}\n")
            log_file.write(f"User Input: {user_input}\n")
            log_file.write(f"Ada's Response:\n{ada_response}\n\n")
        print("\n" + "-"*50)  # Add a separator line

if __name__ == "__main__":
    asyncio.run(main())
