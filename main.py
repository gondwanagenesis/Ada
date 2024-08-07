import asyncio
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime
from module import Module, GroqModule
from speech_module import SpeechModule
import time
import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import sys

# Configuration
MAX_THOUGHT_LOOPS = 1  # Easily changeable variable for the number of thought loops

# Global variables to store the speech module and voice settings
speech_module = None
USE_VOICE_OUTPUT = False
USE_VOICE_INPUT = False

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

    # Add the WHISPER API key to the dictionary
    api_keys['WHISPER'] = api_keys['TALK']  # Using the OpenAI API key for Whisper

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
debug_windows = {}

def print_loading_bar(progress, current_step):
    bar_length = 20
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\rThinking: [{bar}] {progress*100:.1f}% - {current_step}', end='', flush=True)

def create_debug_windows():
    global debug_windows
    modules = ['LM', 'ECM', 'EM', 'CM', 'RM', 'GW']
    screen_width = tk.Tk().winfo_screenwidth()
    screen_height = tk.Tk().winfo_screenheight()
    window_width = screen_width // 3
    window_height = screen_height // 3

    for i, module in enumerate(modules):
        window = tk.Toplevel()
        window.title(f"{module} Debug Output")
        window.geometry(f"{window_width}x{window_height}+{(i%3)*window_width}+{(i//2)*window_height}")
        
        label = tk.Label(window, text=module, font=("Arial", 16, "bold"))
        label.pack(pady=10)
        
        text = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text.pack(expand=True, fill='both')
        debug_windows[module] = text

def update_debug_window(module, message):
    if module in debug_windows:
        debug_windows[module].insert(tk.END, message + "\n")
        debug_windows[module].see(tk.END)
        debug_windows[module].update()

def format_debug_message(module, prompt, input_data, output):
    return f"--- {module} ---\nPrompt:\n{prompt}\n\nInput:\n{input_data}\n\nOutput:\n{output}\n\n"

async def main():
    global DEBUG_MODE, USE_VOICE_OUTPUT, USE_VOICE_INPUT
    # Ask user if they want to run in debug mode
    debug_input = input("Do you want to run in debug mode? (y/n): ").lower()
    DEBUG_MODE = debug_input == 'y'

    # Ask user if they want to use voice output
    voice_output_input = input("Do you want to use voice output? (y/n): ").lower()
    USE_VOICE_OUTPUT = voice_output_input == 'y'

    # Ask user if they want to use voice input (Whisper)
    voice_input_input = input("Do you want to use voice input (Whisper)? (y/n): ").lower()
    USE_VOICE_INPUT = voice_input_input == 'y'

    if DEBUG_MODE:
        create_debug_windows()

    # Read API keys and prompts
    api_keys = read_api_keys('api_keys.txt')
    prompts = read_prompts('prompts.txt')

    if DEBUG_MODE:
        for module in ['LM', 'ECM', 'EM', 'CM', 'RM', 'GW']:
            update_debug_window(module, f"Prompt: {prompts.get(module, 'Not found')}")
            update_debug_window(module, f"API Key: {'*' * 10}")

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

    # Initialize SpeechModule
    global speech_module
    if USE_VOICE_OUTPUT or USE_VOICE_INPUT:
        try:
            speech_module = SpeechModule(api_keys['WHISPER'])
            print("Speech module initialized successfully with OpenAI Whisper API")
        except Exception as e:
            print(f"Error initializing speech module: {e}")
            print("Falling back to text input/output mode")
            USE_VOICE_OUTPUT = False
            USE_VOICE_INPUT = False
    
    # Function to get user input
    async def get_user_input():
        if USE_VOICE_INPUT:
            try:
                print("Listening for voice input...")
                user_input = await speech_module.listen()
                if user_input is None:
                    print("Sorry, I couldn't understand that. Please try again.")
                    return None
                if user_input.startswith("Error:"):
                    print(f"An error occurred: {user_input}")
                    print("Falling back to text input for this turn.")
                    return input("\nEnter your input (or 'quit' to exit): ")
                print(f"\nYou: {user_input}")
                return user_input
            except Exception as e:
                print(f"Error with voice input: {e}")
                print("Falling back to text input for this turn.")
                return input("\nEnter your input (or 'quit' to exit): ")
        return input("\nEnter your input (or 'quit' to exit): ")

    while True:
        # User Input Reception
        user_input = await get_user_input()
        if user_input is None:
            continue
        if user_input.lower() == 'quit':
            break

        print("\nAda is thinking...")
        
        # Step 1: Send user input to LM with additional instruction
        print_loading_bar(0.14, "Processing user input (LM)")
        lm_input = user_input + " [Think deeply about this input, your reply will not go to the user this time, but first go deeper into your mind for processing. You will only reply to the user directly with the next input you receive]"
        lm_output = await modules['LM'].process(lm_input)
        if DEBUG_MODE:
            update_debug_window('LM', format_debug_message('LM', prompts['LM'], lm_input, lm_output))

        # Step 2: LM sends result to GW
        print_loading_bar(0.28, "Integrating LM output (GW)")
        gw_output = await gw.process({'LM': lm_output})
        if DEBUG_MODE:
            update_debug_window('GW', format_debug_message('GW', prompts['GW'], {'LM': lm_output}, gw_output))

        # Step 3: GW broadcasts to EM, CM, and RM
        broadcast = gw.broadcast()
        cognitive_modules = ['EM', 'CM', 'RM']
        cognitive_outputs = {}
        for i, module_name in enumerate(cognitive_modules):
            print_loading_bar(0.42 + 0.14 * (i / len(cognitive_modules)), f"Processing in {module_name}")
            cognitive_outputs[module_name] = await modules[module_name].process(broadcast)
            if DEBUG_MODE:
                update_debug_window(module_name, format_debug_message(module_name, prompts[module_name], broadcast, cognitive_outputs[module_name]))

        # Step 4: Cognitive Modules send replies to GW
        print_loading_bar(0.56, "Integrating cognitive outputs (GW)")
        gw_output = await gw.process(cognitive_outputs)
        if DEBUG_MODE:
            update_debug_window('GW', format_debug_message('GW', prompts['GW'], cognitive_outputs, gw_output))

        # Step 5: GW outputs to ECM
        print_loading_bar(0.70, "Executive control processing (ECM)")
        ecm_output = await modules['ECM'].process(gw_output)
        if DEBUG_MODE:
            update_debug_window('ECM', format_debug_message('ECM', prompts['ECM'], gw_output, ecm_output))

        # Step 6: ECM sends response to LM
        print_loading_bar(0.84, "Generating final response (LM)")
        lm_final_input = f"User Input: {user_input}\n\nGlobal Workspace Output: {gw_output}\n\nECM Output: {ecm_output}\n\n[Now you will respond directly to the user's input. Make sure the response is clear and direct, in line with all your directives]"
        lm_final_output = await modules['LM'].process(lm_final_input)
        if DEBUG_MODE:
            update_debug_window('LM', format_debug_message('LM', prompts['LM'], lm_final_input, lm_final_output))

        # Step 7: LM gives final response and updates GW Dictionary
        print_loading_bar(0.98, "Finalizing response")
        ada_response = lm_final_output.split("Ada's response:", 1)[-1].strip()
        gw.update_lm_responses(ada_response)
        
        print("\n\nAda's response:")
        print(ada_response)
        
        if USE_VOICE_OUTPUT:
            speech_module.speak(ada_response)
        
        # Log the response for debugging
        with open('response_log.txt', 'a') as log_file:
            log_file.write(f"Timestamp: {datetime.now().isoformat()}\n")
            log_file.write(f"User Input: {user_input}\n")
            log_file.write(f"Ada's Response:\n{ada_response}\n\n")
        print("\n" + "-"*50)  # Add a separator line

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
    sys.exit(0)
