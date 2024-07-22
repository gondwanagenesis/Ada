import asyncio
from typing import Dict, Any
from datetime import datetime
from module import Module

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

class GlobalWorkspace:
    def __init__(self, prompt: str, api_key: str):
        self.prompt = prompt
        self.api_key = api_key
        self.last_output = None

    async def process(self, module_outputs: Dict[str, str]) -> str:
        """Process module outputs and return a timestamped response."""
        formatted_outputs = "\n".join([f"{module}: {output}" for module, output in module_outputs.items()])
        input_data = f"{self.prompt}\n\nModule Outputs:\n{formatted_outputs}"
        
        # Simulating API call
        response = f"Processed by Global Workspace: {input_data}"
        
        timestamp = datetime.now().isoformat()
        self.last_output = f"[{timestamp}] {response}"
        return self.last_output

    def broadcast(self) -> str:
        """Return the most recent Global Workspace output."""
        return self.last_output

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
        user_input = input("Enter your input (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break

        # Update PIM with user input
        pim_output = await modules['PIM'].process(user_input)
        print(f"PIM processed input: {pim_output}")

        continue_thinking = True
        while continue_thinking:
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
                print(f"{module_name} output: {output}")

            # Global Workspace Processing
            gw_output = await gw.process(module_outputs)
            print(f"Global Workspace output: {gw_output}")

            # Broadcast GW output
            broadcast = gw.broadcast()
            print(f"Broadcasting: {broadcast}")

            # ECM decides whether to continue thinking or generate response
            ecm_decision = await modules['ECM'].process(broadcast)
            continue_thinking = 'continue' in ecm_decision.lower()
            print(f"ECM decision: {ecm_decision}")

        # Response Generation
        response = await modules['RGM'].process(broadcast)
        print(f"Generated response: {response}")

        # Logging (simplified for this implementation)
        print("Logging: Input and output for each module logged.")

if __name__ == "__main__":
    asyncio.run(main())
