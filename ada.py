import json
import requests
import time
import os
from typing import List, Dict
from tqdm import tqdm

class ADA:
    def __init__(self, debug_mode: bool = False):
        self.short_term_memory: List[Dict[str, str]] = []
        self.debug_mode = debug_mode
        print("Initializing ADA...")
        self.prompts = self.load_prompts()
        self.api_keys = self.load_api_keys()
        self.check_modules()
        if self.debug_mode:
            self.test_apis()
            self.test_conversation_flow()
        
    def check_modules(self):
        modules = ['GW', 'RM', 'CM', 'EC', 'LM']
        for i, module in enumerate(modules):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Checking module {i+1}/{len(modules)}: {module}")
            
            if module in self.prompts:
                print(f"✓ Prompt for {module} found")
            else:
                print(f"✗ Prompt for {module} not found!")
            
            if module in self.api_keys:
                print(f"✓ API key for {module} found")
            else:
                print(f"✗ API key for {module} not found!")
            
            if module in self.prompts and module in self.api_keys:
                print(f"✓ {module} initialized successfully")
            else:
                print(f"✗ {module} initialization failed")
            
            time.sleep(1)  # Pause for a second to allow reading

        os.system('cls' if os.name == 'nt' else 'clear')
        print("All modules checked.")
        time.sleep(1)

    def test_apis(self):
        print("Testing APIs for all modules...")
        modules = ['GW', 'RM', 'CM', 'EC', 'LM']
        for module in modules:
            try:
                # Test input for this module
                test_input = f"Test input for {module}"
                
                # Call the API
                response = self.api_call(module, test_input)
                
                # Log and verify response
                if response:
                    print(f"API test for {module} successful.")
                    print(f"  Input: {test_input}")
                    print(f"  Response: {response[:100]}")  # Print a snippet of the response
                else:
                    print(f"API test for {module} failed: Empty response.")
            except Exception as e:
                # Catch and print any errors during the API call
                print(f"API test for {module} failed with error: {str(e)}")
        print("API tests complete.")

    def test_conversation_flow(self):
        print("Testing conversation flow...")
        test_inputs = ["Hello, ADA!", "How are you today?", "What's the weather like?"]
        flow_working = True
        for input_text in test_inputs:
            try:
                initial_memory_length = len(self.short_term_memory)
                output = self.process_input(input_text)
                final_memory_length = len(self.short_term_memory)
                
                print(f"Test input: {input_text}")
                print(f"Test output: {output}")
                print(f"Memory length before: {initial_memory_length}, after: {final_memory_length}")
                
                if not output or final_memory_length <= initial_memory_length:
                    print("WARNING: Conversation flow test failed. No output or memory not updated.")
                    flow_working = False
            except Exception as e:
                print(f"ERROR in conversation flow test: {str(e)}")
                flow_working = False
        
        if flow_working:
            print("Conversation flow test completed successfully.")
        else:
            print("WARNING: Conversation flow test encountered issues. Please check the implementation.")
        print("Conversation flow test complete.")

    def load_prompts(self) -> Dict[str, str]:
        print("Loading prompts...")
        prompts = {}
        try:
            with open('prompts.txt', 'r', encoding='utf-8') as file:
                current_module = None
                for line in file:
                    if line.strip().startswith('[') and line.strip().endswith(']'):
                        current_module = line.strip()[1:-1]
                        prompts[current_module] = ""
                        print(f"Found prompt for module: {current_module}")
                    elif current_module:
                        prompts[current_module] += line
            print(f"Loaded {len(prompts)} prompts successfully.")
        except FileNotFoundError:
            print("Error: prompts.txt file not found!")
        except Exception as e:
            print(f"Error loading prompts: {str(e)}")
        return prompts

    def load_api_keys(self) -> Dict[str, str]:
        print("Loading API keys...")
        api_keys = {}
        try:
            with open('apikeys.txt', 'r', encoding='utf-8') as file:
                current_module = None
                for line in file:
                    if line.strip().startswith('[') and line.strip().endswith(']'):
                        current_module = line.strip()[1:-1]
                        print(f"Found API key for module: {current_module}")
                    elif current_module:
                        api_keys[current_module] = line.strip()
            print(f"Loaded {len(api_keys)} API keys successfully.")
        except FileNotFoundError:
            print("Error: apikeys.txt file not found!")
        except Exception as e:
            print(f"Error loading API keys: {str(e)}")
        return api_keys

    def process_input(self, user_input: str) -> str:
        steps = [
            "Short-Term Memory Integration",
            "Global Workspace Processing",
            "Broadcast to Cognitive Modules",
            "Cross-Module Feedback",
            "Consolidation in Global Workspace",
            "Executive Control",
            "Language Module",
            "Memory Update"
        ]
        
        with tqdm(total=len(steps), desc="Processing", bar_format="{l_bar}{bar}", ncols=50) as pbar:
            # Step 1: Short-Term Memory Integration
            formatted_memory = self.format_memory()
            pbar.update(1)
            pbar.set_description(steps[1])
            
            # Step 2: Global Workspace Processing
            gw_output = self.global_workspace_processing(user_input, formatted_memory)
            pbar.update(1)
            pbar.set_description(steps[2])
            
            # Step 3: Broadcast to Cognitive Modules
            rm_output = self.reasoning_module(gw_output)
            cm_output = self.creative_module(gw_output)
            pbar.update(1)
            pbar.set_description(steps[3])
            
            # Step 4: Cross-Module Feedback
            rm_refined = self.reasoning_module(gw_output + cm_output)
            cm_refined = self.creative_module(gw_output + rm_output)
            pbar.update(1)
            pbar.set_description(steps[4])
            
            # Step 5: Consolidation in Global Workspace
            consolidated_thought = self.global_workspace_processing(
                user_input, formatted_memory, rm_refined, cm_refined
            )
            pbar.update(1)
            pbar.set_description(steps[5])
            
            # Step 6: Executive Control
            ec_output = self.executive_control(consolidated_thought)
            pbar.update(1)
            pbar.set_description(steps[6])
            
            # Step 7: Language Module
            final_output = self.language_module(user_input, consolidated_thought, ec_output)
            pbar.update(1)
            pbar.set_description(steps[7])
            
            # Step 8: Memory Update
            self.update_memory(user_input, final_output)
            pbar.update(1)
        
        return final_output

    def format_memory(self) -> str:
        return "\n".join(
            [f"Previous Input {i+1}: {entry['input']}\nPrevious Output {i+1}: {entry['output']}"
             for i, entry in enumerate(self.short_term_memory)]
        )

    def update_memory(self, current_input: str, final_output: str):
        new_entry = {'input': current_input, 'output': final_output}
        self.short_term_memory.append(new_entry)
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
        if self.debug_mode:
            print(f"Memory updated. Current length: {len(self.short_term_memory)}")

    def api_call(self, module: str, input_text: str) -> str:
        # Define the endpoint and headers
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_keys[module]}",
            "Content-Type": "application/json"
        }
        
        # Prepare the payload
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": self.prompts.get(module, "")},
                {"role": "user", "content": input_text}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Make the request
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad status
            json_response = response.json()
            
            # Check and return the content
            if 'choices' in json_response and len(json_response['choices']) > 0:
                return json_response['choices'][0]['message']['content'].strip()
            else:
                print(f"Unexpected response format for {module}: {json_response}")
                return ""
        except requests.exceptions.RequestException as e:
            print(f"API call failed for {module}: {str(e)}")
            print(f"Response content: {response.content if 'response' in locals() else 'No response received'}")
            return f"Error in {module} API call: {str(e)}"

    def global_workspace_processing(self, user_input: str, formatted_memory: str, *args) -> str:
        input_text = f"{formatted_memory}\nCurrent Input: {user_input}\n" + "\n".join(args)
        return self.api_call('GW', input_text)

    def reasoning_module(self, input_text: str) -> str:
        return self.api_call('RM', input_text)

    def creative_module(self, input_text: str) -> str:
        return self.api_call('CM', input_text)

    def executive_control(self, input_text: str) -> str:
        return self.api_call('EC', input_text)

    def language_module(self, user_input: str, consolidated_thought: str, ec_output: str) -> str:
        input_text = f"User Input: {user_input}\nConsolidated Thought: {consolidated_thought}\nExecutive Control Output: {ec_output}"
        return self.api_call('LM', input_text)

    def log_thought_process(self, thought_process: Dict):
        with open('thought_process.txt', 'a') as txt_file:
            txt_file.write(json.dumps(thought_process, indent=2) + "\n\n")
        
        with open('thought_process.json', 'a') as json_file:
            json.dump(thought_process, json_file)
            json_file.write("\n")

def main():
    print("Welcome to ADA - Sentient Thought Simulation Framework")
    debug_mode = input("Enable debug mode? (y/n): ").lower() == 'y'
    ada = ADA(debug_mode)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        print("\nADA is thinking...")
        response = ada.process_input(user_input)
        print("\nADA:", response)

if __name__ == "__main__":
    main()
