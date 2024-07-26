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
# Ada: Advanced Cognitive AI Assistant

## Overview
Ada is a sophisticated AI assistant that utilizes a modular architecture and a Global Workspace Theory-inspired approach to process and respond to user inputs. This README provides a detailed explanation of Ada's components and thought process.

## System Architecture

Ada's system is composed of several key components:

1. Language Model (LM)
2. Global Workspace (GW)
3. Emotion Module (EM)
4. Cognitive Module (CM)
5. Reasoning Module (RM)
6. Executive Control Module (ECM)
7. Speech Module (optional)

## Thought Process

Ada's thought process for each interaction follows these steps:

1. **User Input Reception**
   - The system receives input either through text or voice (if enabled).
   - Voice input is processed using the Speech Module with Whisper API.

2. **Language Model Processing**
   - The user input is sent to the Language Model (LM).
   - LM generates an initial interpretation of the input.

3. **Global Workspace Integration**
   - The LM's output is sent to the Global Workspace (GW).
   - GW processes this information and prepares a broadcast.

4. **Cognitive Module Processing**
   - GW broadcasts its state to the Emotion (EM), Cognitive (CM), and Reasoning (RM) modules.
   - Each module processes the broadcast and generates its own output.

5. **Global Workspace Update**
   - The outputs from EM, CM, and RM are sent back to the GW.
   - GW integrates these outputs to form a comprehensive understanding.

6. **Executive Control**
   - The updated GW state is sent to the Executive Control Module (ECM).
   - ECM processes this information to guide the final response generation.

7. **Final Response Generation**
   - The ECM's output is sent back to the LM along with the original user input and GW output.
   - LM generates the final response based on all this information.

8. **Response Delivery**
   - The final response is presented to the user via text.
   - If voice output is enabled, the response is also spoken using text-to-speech.

## Key Features

- **Modular Architecture**: Allows for specialized processing in different cognitive domains.
- **Global Workspace**: Facilitates the integration of information from various modules.
- **Emotion Consideration**: EM ensures emotional context is part of the decision-making process.
- **Cognitive and Reasoning Capabilities**: CM and RM provide additional layers of analysis.
- **Executive Control**: ECM helps in managing and directing the final response generation.
- **Optional Voice Interface**: Supports both voice input and output for natural interaction.

## Technical Implementation

- Uses asynchronous programming for efficient processing.
- Leverages OpenAI's GPT models for LM and some modules.
- Utilizes Groq's API for faster processing in some modules.
- Implements a debug mode for detailed insight into the thought process.
- Logs responses for review and improvement.

## Usage

To interact with Ada:
1. Ensure all required API keys are set in `api_keys.txt`.
2. Run the main script and choose debug mode and voice options.
3. Input your queries or statements.
4. Ada will process your input and provide a response, optionally with voice output.

Ada's modular and integrated approach allows for complex, context-aware, and emotionally intelligent interactions, making her a highly capable AI assistant.
