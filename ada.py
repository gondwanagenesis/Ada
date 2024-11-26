import json
import requests
from typing import List, Dict

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
        print("Checking all modules...")
        modules = ['GW', 'RM', 'CM', 'EC', 'LM']
        for module in modules:
            if module not in self.prompts:
                print(f"Warning: Prompt for {module} not found!")
            if module not in self.api_keys:
                print(f"Warning: API key for {module} not found!")
            if module in self.prompts and module in self.api_keys:
                print(f"Module {module} initialized successfully.")
        print("Module check complete.")

    def test_apis(self):
        print("Testing APIs...")
        modules = ['GW', 'RM', 'CM', 'EC', 'LM']
        for module in modules:
            try:
                response = self.api_call(module, "Test input")
                print(f"API test for {module} successful. Response: {response[:50]}...")
            except Exception as e:
                print(f"API test for {module} failed. Error: {str(e)}")
        print("API tests complete.")

    def test_conversation_flow(self):
        print("Testing conversation flow...")
        test_inputs = ["Hello, ADA!", "How are you today?", "What's the weather like?"]
        for input_text in test_inputs:
            output = self.process_input(input_text)
            print(f"Test input: {input_text}")
            print(f"Test output: {output}")
            print(f"Memory length: {len(self.short_term_memory)}")
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
        if self.debug_mode:
            print(f"Processing input: {user_input}")
        
        # Step 2: Short-Term Memory Integration
        formatted_memory = self.format_memory()
        if self.debug_mode:
            print(f"Formatted memory: {formatted_memory}")
        
        # Step 3: Global Workspace Processing
        gw_output = self.global_workspace_processing(user_input, formatted_memory)
        if self.debug_mode:
            print(f"Global Workspace output: {gw_output}")
        
        # Step 4: Broadcast to Cognitive Modules
        rm_output = self.reasoning_module(gw_output)
        cm_output = self.creative_module(gw_output)
        if self.debug_mode:
            print(f"Reasoning Module output: {rm_output}")
            print(f"Creative Module output: {cm_output}")
        
        # Step 5: Cross-Module Feedback
        rm_refined = self.reasoning_module(gw_output + cm_output)
        cm_refined = self.creative_module(gw_output + rm_output)
        if self.debug_mode:
            print(f"Refined Reasoning Module output: {rm_refined}")
            print(f"Refined Creative Module output: {cm_refined}")
        
        # Step 6: Consolidation in Global Workspace
        consolidated_thought = self.global_workspace_processing(
            user_input, formatted_memory, rm_refined, cm_refined
        )
        if self.debug_mode:
            print(f"Consolidated thought: {consolidated_thought}")
        
        # Step 7: Executive Control
        ec_output = self.executive_control(consolidated_thought)
        if self.debug_mode:
            print(f"Executive Control output: {ec_output}")
        
        # Step 8: Language Module
        final_output = self.language_module(user_input, consolidated_thought, ec_output)
        if self.debug_mode:
            print(f"Final output: {final_output}")
        
        # Step 9: User Output
        self.update_memory(user_input, final_output)
        
        # Step 10: Memory Update (already done in update_memory)
        
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
        url = "https://api.groq.com/v1/process"
        headers = {
            "Authorization": f"Bearer {self.api_keys[module]}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-2-model",
            "input": f"{self.prompts[module]}\n\nInput: {input_text}"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            json_response = response.json()
            if self.debug_mode:
                print(f"API Response for {module}: {json_response}")
            if 'output' in json_response:
                return json_response['output']
            elif 'choices' in json_response and len(json_response['choices']) > 0:
                return json_response['choices'][0]['text']
            else:
                raise KeyError("Unexpected response format")
        except requests.exceptions.RequestException as e:
            print(f"API call failed for {module}: {str(e)}")
            return f"Error in {module} API call: {str(e)}"
        except KeyError as e:
            print(f"Unexpected response format for {module}: {str(e)}")
            return f"Error in {module} response format: {str(e)}"

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
        
        response = ada.process_input(user_input)
        print("ADA:", response)

if __name__ == "__main__":
    main()
