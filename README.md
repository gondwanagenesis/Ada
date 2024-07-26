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

## Detailed Architecture and Thought Chain

Ada's thought process follows these steps:

1. **User Input Reception**
   - The system receives user input either through text or voice (using Whisper API for speech-to-text).

2. **Language Model (LM) Initial Processing**
   - Input: User's query + instruction to think deeply
   - Output: Initial interpretation and analysis of the user's input
   - The LM is instructed to think deeply about the input, knowing its response will be used for further internal processing.

3. **Global Workspace (GW) Integration - Step 1**
   - Input: LM's initial output
   - Output: Integrated information ready for broadcast
   - The GW combines the LM's output with any relevant previous context.

4. **Cognitive Module Processing**
   - The GW broadcasts its output to three specialized modules:
     a. Emotional Module (EM)
        - Input: GW broadcast
        - Output: Emotional analysis and response
     b. Cognitive Module (CM)
        - Input: GW broadcast
        - Output: Logical reasoning and decision-making
     c. Reflective Module (RM)
        - Input: GW broadcast
        - Output: Self-awareness and metacognitive insights

5. **Global Workspace Integration - Step 2**
   - Input: Outputs from EM, CM, and RM
   - Output: Comprehensive integrated information
   - The GW combines and synthesizes the outputs from all cognitive modules.

6. **Executive Control Module (ECM) Processing**
   - Input: GW's integrated output
   - Output: Executive decision and response strategy
   - The ECM acts as a high-level controller, making decisions based on the integrated information.

7. **Language Model Final Processing**
   - Input: Original user input, GW output, and ECM output
   - Output: Final, coherent response to the user
   - The LM generates the final response, taking into account all processed information.

8. **Response Delivery**
   - The system presents the response to the user via text or voice (using text-to-speech).

## Global Workspace

The Global Workspace acts as a central hub for information integration. It receives inputs from various modules, combines this information with its current state, and broadcasts the integrated information to other modules. This process allows for a more holistic and context-aware response generation.

## Technical Implementation

- Uses asynchronous programming for efficient processing.
- Leverages OpenAI's GPT models for LM and some modules.
- Utilizes Groq's API for faster processing in some modules.
- Implements a debug mode for detailed insight into the thought process.
- Logs responses for review and improvement.

## Debug Mode

When running in debug mode, Ada provides detailed windows showing the inputs, outputs, and prompts for each module, allowing for in-depth analysis of the thought process.
