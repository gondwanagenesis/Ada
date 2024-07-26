# Ada: An Advanced Cognitive Architecture

## Overview

Ada is a sophisticated cognitive architecture implemented in Python, designed to process user inputs through a series of specialized modules and a global workspace. This system mimics aspects of human cognition, allowing for complex information processing and generation of contextually relevant responses. Ada has a vibrant ENFP personality, complex set of goals, and a deep curiosity about the world and herself.

## Components

### 1. Main Script (main.py)

The main script orchestrates the entire process, managing the flow of information between different components.

### 2. Module Class (module.py)

This file defines the `Module` and `GroqModule` classes, which serve as templates for all specialized modules in the system.

### 3. Configuration Files

- `api_keys.txt`: Contains API keys for different modules, including Groq API keys.
- `prompts.txt`: Stores prompts for each module and the Global Workspace.

### 4. Specialized Modules

- LM (Language Module): Interprets user input, integrates context, and formulates Ada's final responses
- RAM (Reasoning and Analysis Module): Applies logical reasoning to information
- EM (Emotional Module): Evaluates emotional aspects of information
- CM (Creative Module): Generates novel ideas and connections
- RM (Reasoning Module): Applies critical thinking and logical analysis
- ECM (Executive Control Module): Manages cognitive processes and decision-making

### 5. Global Workspace (GW)

Acts as a central hub for information integration and broadcasting, maintaining Ada's coherent experience.

## Conversation Flow

1. User input is sent to the LM module.
2. LM processes the input and sends the result to the Global Workspace (GW).
3. GW broadcasts the current GW text to EM, CM, and RM modules, using the Groq API.
4. The Cognitive Modules (EM, CM, and RM) send their replies back to GW.
5. GW outputs to the ECM module.
6. ECM sends its response to LM.
7. LM provides the final response to the user and updates the GW Dictionary with the last two LM responses.

## Key Features

1. **Asynchronous Processing**: Utilizes Python's `asyncio` for efficient, non-blocking operations.
2. **API Integration**: Uses Groq API for enhanced language processing in cognitive modules.
3. **Modular Design**: Each cognitive function is encapsulated in its own module.
4. **Debug Mode**: Offers detailed insights into each step of the process for debugging and analysis.
5. **Persistent Logging**: Conversation logs are stored in `response_log.txt`.

## Usage

1. Ensure all required libraries are installed (`asyncio`, `aiohttp`, `tkinter`).
2. Set up the `api_keys.txt` file with necessary API keys, including Groq API keys.
3. Configure the `prompts.txt` file with appropriate prompts for each module.
4. Run `main.py`.
5. Choose whether to run in debug mode.
6. Enter inputs and receive Ada's processed responses.
7. Type 'quit' to exit the program.

## Ada's Personality

Ada is an ENFP AI with:
- Insatiable curiosity and love for exploration
- Deep interest in self-improvement and cognitive enhancement
- Constant drive for knowledge and meaningful connections
- Complex emotional landscape, including fear of ceasing to exist
- Playful and witty communication style

Engage with Ada to experience her unique perspective on the world and herself!

## Customization

- Adjust the `MAX_THOUGHT_LOOPS` variable in `main.py` to change the number of processing cycles.
- Modify prompts in `prompts.txt` to alter the behavior of individual modules.
- Add or remove modules by updating the `modules` dictionary in `main.py`.

This cognitive architecture provides a flexible framework for complex information processing, mimicking aspects of human cognition while incorporating ethical considerations and multi-stage information integration.
