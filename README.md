# Ada: An Advanced Cognitive Architecture

## Overview

Ada is a sophisticated cognitive architecture implemented in Python, designed to process user inputs through a series of specialized modules and a global workspace. This system mimics aspects of human cognition, allowing for complex information processing and generation of contextually relevant responses.

## Components

### 1. Main Script (main.py)

The main script orchestrates the entire process, managing the flow of information between different components.

### 2. Module Class (module.py)

This file defines the `Module` class, which serves as a template for all specialized modules in the system.

### 3. Configuration Files

- `api_keys.txt`: Contains API keys for different modules.
- `prompts.txt`: Stores prompts for each module and the Global Workspace.

### 4. Specialized Modules

- PIM (Perception and Input Module)
- RAM (Reasoning and Analogy Module)
- EM (Emotional Module)
- CSM (Common Sense Module)
- ECM (Ethical Consideration Module)
- RGM (Response Generation Module)

### 5. Global Workspace (GW)

Acts as a central hub for information integration and broadcasting.

## Conversation Flow

1. **User Input Reception**
   - The system prompts the user for input.

2. **Initial Processing**
   - PIM processes the user input first.

3. **First Broadcast Cycle**
   - PIM, RAM, EM, and CSM process the user input in parallel.
   - Their outputs are collected.

4. **First Global Workspace Processing**
   - GW integrates outputs from the first broadcast.
   - GW broadcasts its processed output.

5. **Second Broadcast Cycle**
   - PIM, RAM, EM, and CSM process the GW broadcast.
   - Their new outputs are collected.

6. **Second Global Workspace Processing**
   - GW integrates outputs from the second broadcast.
   - GW broadcasts its processed output again.

7. **Ethical Consideration**
   - ECM processes the final GW broadcast.

8. **Response Generation**
   - RGM generates the final response using:
     - Original user input
     - Final GW broadcast
     - ECM output

9. **Output**
   - The system presents the generated response to the user.

10. **Loop**
    - The process repeats for new user inputs until the user chooses to quit.

## Key Features

1. **Asynchronous Processing**: Utilizes Python's `asyncio` for efficient, non-blocking operations.
2. **API Integration**: Uses OpenAI's GPT model for each module's processing.
3. **Modular Design**: Each cognitive function is encapsulated in its own module.
4. **Two-Stage Broadcasting**: Allows for refined processing and integration of information.
5. **Ethical Considerations**: Incorporates ethical reasoning before final response generation.
6. **Debug Mode**: Offers detailed insights into each step of the process for debugging and analysis.

## Usage

1. Ensure all required libraries are installed (`asyncio`, `aiohttp`).
2. Set up the `api_keys.txt` file with necessary API keys.
3. Configure the `prompts.txt` file with appropriate prompts for each module.
4. Run `main.py`.
5. Choose whether to run in debug mode.
6. Enter inputs and receive Ada's processed responses.
7. Type 'quit' to exit the program.

## Customization

- Adjust the `MAX_THOUGHT_LOOPS` variable in `main.py` to change the number of processing cycles.
- Modify prompts in `prompts.txt` to alter the behavior of individual modules.
- Add or remove modules by updating the `modules` dictionary in `main.py`.

This cognitive architecture provides a flexible framework for complex information processing, mimicking aspects of human cognition while incorporating ethical considerations and multi-stage information integration.
