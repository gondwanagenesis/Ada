from typing import Any

class Module:
    def __init__(self, name: str, prompt: str, api_key: str):
        self.name = name
        self.prompt = prompt
        self.api_key = api_key

    async def process(self, input_data: Any) -> str:
        """
        Process input data using the module's prompt and API key.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            str: The processed output.
        """
        # Prepend module's prompt to input_data
        full_input = f"{self.prompt}\n\nInput: {input_data}"
        
        # Simulating API call using the module's api_key
        # In a real implementation, this would be an actual API call
        output = f"Processed by {self.name}: {full_input}"
        
        return output
