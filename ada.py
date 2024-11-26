import json
import requests
from typing import List, Dict

class ADA:
    def __init__(self, debug_mode: bool = False):
        self.short_term_memory: List[Dict[str, str]] = []
        self.debug_mode = debug_mode
        self.prompts = self.load_prompts()
        self.api_keys = self.load_api_keys()

    def load_prompts(self) -> Dict[str, str]:
        prompts = {}
        with open('prompts.txt', 'r') as file:
            current_module = None
            for line in file:
                if line.strip().startswith('[') and line.strip().endswith(']'):
                    current_module = line.strip()[1:-1]
                    prompts[current_module] = ""
                elif current_module:
                    prompts[current_module] += line
        return prompts

    def load_api_keys(self) -> Dict[str, str]:
        api_keys = {}
        with open('apikeys.txt', 'r') as file:
            current_module = None
            for line in file:
                if line.strip().startswith('[') and line.strip().endswith(']'):
                    current_module = line.strip()[1:-1]
                elif current_module:
                    api_keys[current_module] = line.strip()
        return api_keys

    def process_input(self, user_input: str) -> str:
        # Step 2: Short-Term Memory Integration
        formatted_memory = self.format_memory()
        
        # Step 3: Global Workspace Processing
        gw_output = self.global_workspace_processing(user_input, formatted_memory)
        
        # Step 4: Broadcast to Cognitive Modules
        rm_output = self.reasoning_module(gw_output)
        cm_output = self.creative_module(gw_output)
        
        # Step 5: Cross-Module Feedback
        rm_refined = self.reasoning_module(gw_output + cm_output)
        cm_refined = self.creative_module(gw_output + rm_output)
        
        # Step 6: Consolidation in Global Workspace
        consolidated_thought = self.global_workspace_processing(
            user_input, formatted_memory, rm_refined, cm_refined
        )
        
        # Step 7: Executive Control
        ec_output = self.executive_control(consolidated_thought)
        
        # Step 8: Language Module
        final_output = self.language_module(user_input, consolidated_thought, ec_output)
        
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
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['output']

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
