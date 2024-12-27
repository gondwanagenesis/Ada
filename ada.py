import json
import asyncio
import aiohttp
import time
import os
from typing import List, Dict
from tqdm.asyncio import tqdm
import logging
import re

class ADAAsync:
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the ADA chatbot with optional debug mode.
        Loads prompts and API keys, initializes the session, resets logs, and runs initial tests.
        """
        self.short_term_memory: List[Dict[str, str]] = []
        self.debug_mode = debug_mode
        self.prompts = self.load_prompts()
        self.api_keys = self.load_api_keys()
        self.session = None  # To be initialized in async context

        # Reset logs at startup
        self.reset_logs()
        
        # Display title screen
        self.display_title_screen()

    def reset_logs(self):
        """
        Resets the log files at the start of the program.
        """
        open('ada_performance.log', 'w').close()
        open('thought_process.txt', 'w').close()
        open('thought_process.json', 'w').close()

    def display_title_screen(self):
        """
        Displays an ASCII art title screen for ADA that persists.
        """
        print(r"""
█████╗ ██████╗  █████╗ 
██╔══██╗██╔══██╗██╔══██╗
███████║██║  ██║███████║
██╔══██║██║  ██║██╔══██║
██║  ██║██████╔╝██║  ██║
╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
                                                   
Ada: Synthetic Life
        """)

    def run_initial_tests(self):
        """
        Runs module checks quietly and displays 'All systems passed.' at the end.
        """
        if self.debug_mode:
            self.check_modules()
            self.test_apis()
            self.test_conversation_flow()
            input("Debug tests completed. Press Enter to continue...")
        else:
            self.check_modules_quiet()
            print("All systems passed.")

    def check_modules_quiet(self):
        """
        Quietly checks modules without leaving residual text on the screen.
        """
        modules = ['GW', 'RM', 'CM', 'EC', 'LM']
        for module in modules:
            print(f"Checking module: {module}", end='\r', flush=True)
            time.sleep(0.1)  # Simulate quick check
        # Clear the line after checks
        print(' ' * 50, end='\r')

    def load_prompts(self) -> Dict[str, str]:
        """
        Loads module-specific prompts from prompts.txt.
        Returns a dictionary with module codes as keys and prompts as values.
        """
        prompts = {}
        try:
            with open('prompts.txt', 'r', encoding='utf-8') as file:
                current_module = None
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_module = line[1:-1]
                        prompts[current_module] = ""
                    elif current_module is not None:
                        prompts[current_module] += line + "\n"
            return prompts
        except FileNotFoundError:
            print("Error: prompts.txt file not found!")
            exit(1)
        except Exception as e:
            print(f"Error loading prompts: {str(e)}")
            exit(1)

    def load_api_keys(self) -> Dict[str, str]:
        """
        Loads API keys for each module from apikeys.txt.
        Returns a dictionary with module codes as keys and API keys as values.
        """
        api_keys = {}
        try:
            with open('apikeys.txt', 'r', encoding='utf-8') as file:
                current_module = None
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_module = line[1:-1]
                    elif current_module and line:
                        api_keys[current_module] = line
                        current_module = None
            return api_keys
        except FileNotFoundError:
            print("Error: apikeys.txt file not found!")
            exit(1)
        except Exception as e:
            print(f"Error loading API keys: {str(e)}")
            exit(1)

    async def initialize(self):
        """hi ada
        Initializes the aiohttp session and runs initial tests.
        """
        self.session = aiohttp.ClientSession()
        self.run_initial_tests()

    async def process_input_async(self, user_input: str) -> str:
        """
        Processes the user's input through the cognitive modules and returns ADA's response.
        """
        total_start_time = time.time()
        step_times = {}
        logging.info(f"Processing input: {user_input}")

        # Step 1: Short-Term Memory Integration
        start_time = time.time()
        formatted_memory = self.format_memory()
        step_times['Memory Integration'] = time.time() - start_time

        # Initialize progress bar
        progress_steps = 7
        pbar = tqdm(total=progress_steps, desc="Processing", unit="step", leave=False)

        # Step 2: Global Workspace Processing
        pbar.set_description("Processing: Global Workspace")
        start_time = time.time()
        gw_output = await self.api_call_async('GW', f"{formatted_memory}\nCurrent Input:\n{user_input}")
        gw_output = self.clean_module_output(gw_output)
        step_times['Global Workspace'] = time.time() - start_time
        pbar.update(1)

        # Steps 3 & 4: Reasoning Module and Creative Module in Parallel (First Pass)
        pbar.set_description("Processing: RM and CM (First Pass)")
        start_time = time.time()
        rm_future1 = asyncio.create_task(self.api_call_async('RM', gw_output))
        cm_future1 = asyncio.create_task(self.api_call_async('CM', gw_output))
        rm_output1, cm_output1 = await asyncio.gather(rm_future1, cm_future1)
        rm_output1 = self.clean_module_output(rm_output1)
        cm_output1 = self.clean_module_output(cm_output1)
        step_times['RM and CM First Pass'] = time.time() - start_time
        pbar.update(1)

        # Steps 3 & 4: Reasoning Module and Creative Module in Parallel (Second Pass)
        pbar.set_description("Processing: RM and CM (Second Pass)")
        start_time = time.time()
        rm_future2 = asyncio.create_task(self.api_call_async('RM', f"Creative Module Output:\n{cm_output1}"))
        cm_future2 = asyncio.create_task(self.api_call_async('CM', f"Reasoning Module Output:\n{rm_output1}"))
        rm_output = self.clean_module_output(await rm_future2)
        cm_output = self.clean_module_output(await cm_future2)
        step_times['RM and CM Second Pass'] = time.time() - start_time
        pbar.update(1)

        # Step 5: Executive Control
        pbar.set_description("Processing: Executive Control")
        start_time = time.time()
        ec_output = self.clean_module_output(await self.api_call_async('EC', f"Reasoning Module Output:\n{rm_output}\n\nCreative Module Output:\n{cm_output}"))
        step_times['Executive Control'] = time.time() - start_time
        pbar.update(1)

        # Step 6: Consolidation in Global Workspace
        pbar.set_description("Processing: Consolidation")
        start_time = time.time()
        consolidated_thought = self.clean_module_output(await self.api_call_async('GW', f"Global Workspace Output:\n{gw_output}\n\nReasoning Module Output:\n{rm_output}\n\nCreative Module Output:\n{cm_output}\n\nExecutive Control Output:\n{ec_output}"))
        step_times['Consolidation'] = time.time() - start_time
        pbar.update(1)

        # Step 7: Language Module
        pbar.set_description("Processing: Language Module")
        start_time = time.time()
        lm_output = self.clean_module_output(await self.api_call_async('LM', f"User Input:\n{user_input}\n\nConsolidated Thought:\n{consolidated_thought}\n\nAs the Language Module, generate a direct and natural response to the user without including any internal thoughts or module outputs."))
        step_times['Language Module'] = time.time() - start_time
        pbar.update(1)

        # Close the progress bar
        pbar.close()

        # Step 8: Memory Update
        start_time = time.time()
        self.update_memory(user_input, lm_output)
        step_times['Memory Update'] = time.time() - start_time

        # Total processing time
        total_time = time.time() - total_start_time
        step_times['Total'] = total_time

        # Log performance
        logging.info("Processing times (in seconds):")
        for step, duration in step_times.items():
            logging.info(f"{step}: {duration:.4f} seconds")

        # Log thought process
        thought_process = {
            "user_input": user_input,
            "gw_output": {"input": formatted_memory + "\nCurrent Input:\n" + user_input, "output": gw_output},
            "rm_output": {"input": gw_output, "output": rm_output},
            "cm_output": {"input": gw_output, "output": cm_output},
            "ec_output": {"input": f"Reasoning Module Output:\n{rm_output}\n\nCreative Module Output:\n{cm_output}", "output": ec_output},
            "consolidated_thought": {"input": f"Global Workspace Output:\n{gw_output}\n\nReasoning Module Output:\n{rm_output}\n\nCreative Module Output:\n{cm_output}\n\nExecutive Control Output:\n{ec_output}", "output": consolidated_thought},
            "lm_output": {"input": f"User Input:\n{user_input}\n\nConsolidated Thought:\n{consolidated_thought}\n\nAs the Language Module, generate a direct and natural response to the user without including any internal thoughts or module outputs.", "output": lm_output},
            "final_output": lm_output  # Ensures only LM's output is considered final
        }
        self.log_thought_process(thought_process)

        return lm_output

    def format_memory(self) -> str:
        """
        Formats the short-term memory into a readable string for context.
        """
        formatted_entries = [
            f"Previous Input {i+1}: {entry['input']}\nPrevious Output {i+1}: {entry['output']}"
            for i, entry in enumerate(self.short_term_memory)
        ]
        return "\n".join(formatted_entries)

    def update_memory(self, current_input: str, final_output: str):
        """
        Updates the short-term memory with the latest interaction.
        Maintains a maximum of 10 entries.
        """
        new_entry = {'input': current_input, 'output': final_output}
        self.short_term_memory.append(new_entry)
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
        if self.debug_mode:
            print(f"Memory updated. Current memory size: {len(self.short_term_memory)}")

    async def api_call_async(self, module: str, input_text: str) -> str:
        """
        Asynchronous API call to the specified module with the given input text.
        Handles retries and exceptions for robustness.
        """
        start_time = time.time()
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_keys.get(module, '')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": self.prompts.get(module, "")},
                {"role": "user", "content": input_text}
            ],
            "max_tokens": 150,  # Reduced for faster responses
            "temperature": 0.7,
            "stop": ["[", "]", "You are", "Your role is"]
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.session.post(url, headers=headers, json=payload, timeout=30) as response:
                    response.raise_for_status()
                    json_response = await response.json()
                    if 'choices' in json_response and json_response['choices']:
                        content = json_response['choices'][0]['message']['content'].strip()
                        api_call_time = time.time() - start_time
                        logging.info(f"API call to {module} took {api_call_time:.4f} seconds")
                        return content
                    else:
                        raise ValueError(f"Invalid response structure: {json_response}")
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Attempt {attempt + 1} failed for {module}: {e}. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    error_message = f"Error in {module} API call: {str(e)}"
                    logging.error(error_message)
                    if self.debug_mode:
                        print(error_message)
                    return error_message

    def log_thought_process(self, thought_process: Dict):
        """
        Logs the thought process to text and JSON files for debugging and analysis.
        """
        # Human-readable log
        with open('thought_process.txt', 'a', encoding='utf-8') as txt_file:
            txt_file.write(f"Thought Process at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for key, value in thought_process.items():
                if isinstance(value, dict) and 'input' in value and 'output' in value:
                    txt_file.write(f"{key} Input:\n{value['input']}\n")
                    txt_file.write(f"{key} Output:\n{value['output']}\n\n")
                else:
                    txt_file.write(f"{key}:\n{value}\n\n")
            txt_file.write("=" * 50 + "\n\n")

        # JSON log
        with open('thought_process.json', 'a', encoding='utf-8') as json_file:
            json.dump(thought_process, json_file, ensure_ascii=False)
            json_file.write("\n")

    def clean_module_output(self, output: str) -> str:
        """
        Cleans the module output by removing any prompts, system messages, or disallowed content.
        """
        # Remove any content that looks like a prompt or system message
        output = re.sub(r'\[.*?\]', '', output)  # Remove text within brackets
        output = re.sub(r'(You are|Your role is|For each input:).*', '', output, flags=re.DOTALL)
        output = output.strip()
        return output

    async def close(self):
        """
        Closes the aiohttp session.
        """
        if self.session:
            await self.session.close()

async def main_async():
    """
    Asynchronous main function to run the ADA chatbot.
    Handles user interaction and initializes the ADA instance.
    """
    ada = ADAAsync(debug_mode=False)
    await ada.initialize()

    try:
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            print("ADA is processing your input...")
            response = await ada.process_input_async(user_input)
            print(f"\nADA: {response}")
    finally:
        await ada.close()

if __name__ == "__main__":
    asyncio.run(main_async())
