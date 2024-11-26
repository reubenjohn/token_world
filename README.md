# token_world

[![codecov](https://codecov.io/gh/reubenjohn/token_world/branch/main/graph/badge.svg?token=token_world_token_here)](https://codecov.io/gh/reubenjohn/token_world/branch/main)
[![CI](https://github.com/reubenjohn/token_world/actions/workflows/main.yml/badge.svg)](https://github.com/reubenjohn/token_world/actions/workflows/main.yml)

A multi-agent simulation leveraging large language models to create dynamic, flexible environments for studying agentic interactions. Designed for researchers, developers, and hobbyists seeking to explore emergent behaviors and complex systems.

## Introduction

**Token World** is a dynamic, multi-agent simulation framework powered by large language models. Designed with flexibility in mind, the project enables the creation of diverse, open-ended environments where agents interact, evolve, and discover, mimicking complex real-world systems.  

The simulation is built for developers, researchers, and enthusiasts exploring the intersections of artificial intelligence, social dynamics, and agent-based modeling. Whether you're simulating a bustling small-town community or creating intricate role-playing game scenarios, **Token World** offers the tools and grounding mechanisms to make interactions logical and meaningful.

### **Key Goals**
1. **Flexibility**: Adapt the framework to simulate various environments and scenarios with minimal customization effort.
2. **Grounding**: Ensure agent actions remain logical and rooted in the environment to reduce hallucinations.
3. **Partial Observability**: Introduce realistic discovery and exploration dynamics, making simulations more engaging and lifelike.
4. **Ease of Use**: Aimed at lowering barriers for experimentation with large language models in agentic workflows.

### **Why It Matters**
By combining cutting-edge AI capabilities with a robust simulation environment, this project inspires developers to push boundaries and explore emergent behaviors in multi-agent systems. It’s not just a framework; it’s a learning experience designed to empower creativity and innovation in AI-driven simulations.

## Features

**Token World** includes a range of technical features that make it a powerful framework for multi-agent simulations (*most or all of these features have **not** been implemented are are only included for documentation purposes*):

1. **Entity-Based Environment**  
   - Every object in the simulation is represented as an entity with unique properties stored in an SQLite database.
   - Supports dynamic state updates and seamless entity interactions validated through precondition checks.

1. **Agentic Interactions**  
   - Agents generate natural language actions that are translated into executable operations.
   - A modular action pipeline ensures each action's feasibility before execution, using grounding mechanisms to validate preconditions and apply effects.

1. **Delegated Action Handling**  
   - Specialized sub-agents handle specific types of interactions (e.g., spatial navigation, item manipulation), ensuring efficiency and extensibility in task execution.

1. **Partial Observability Framework**  
   - Agents operate with limited knowledge of their environment.
   - Information discovery is modeled through interactions, enabling realistic exploration and goal-driven behaviors.

1. **Dynamic Mechanics Generation**  
   - The simulation evolves dynamically, with new mechanics generated on demand based on the agents' actions. This allows the environment to grow and adapt in response to the agents' behaviors, making each run unique.  
   - This feature parallels the concept of "observer effect" in physics, where the state of a system materializes upon interaction, akin to the idea that "reality doesn't exist until observed."
1. **Web-Based Debugging Tool**  
   - Provides an interactive interface to inspect agent interactions and entity states in real time.
   - Facilitates debugging and transparency for developers working on complex simulations.

1. **Extensible Design**  
   - Modular architecture allows for the addition of custom agents, actions, and environments.
   - Easily integrates with different LLM backends, including lightweight local models.

1. **Scalable Simulations**  
   - Optimized to run small to medium-scale simulations on personal laptops with support for larger simulations on more powerful systems.

1. **Interpretable Logging**  
   - All interactions and state changes are logged, enabling detailed analysis of agent behaviors and environment dynamics.

## Examples

- **Scenario 1:** Small-town simulation.
- **Scenario 2:** Role-playing game setup.
- **Scenario 3:** Custom experimental environment for testing agentic workflows.

## Setup

For instructions on setting up the project for development and contributions, see [CONTRIBUTING.md](CONTRIBUTING.md)

To set up the environment variables, create a `.env` file in the root directory of your project (See [.env.example](.env.example)) and add the following lines:

```shell
OPENAI_BASE_URL=https://your_openai_endpoint
OPENAI_API_KEY=your_openai_api_key_here
```

Note that the OpenAI endpoint can be any endpoint that implements the OpenAI API (eg. Ollama).
Alternatively, you can provide the `--openai_base_url` and `--openai_api_key` arguments when running the CLI:

```bash
$ python -m token_world --openai_base_url http://192.168.1.199:11434/v1 --openai_api_key your_openai_api_key_here
#or
$ token_world --openai_base_url http://192.168.1.199:11434/v1 --openai_api_key your_openai_api_key_here
```

## Usage

```py
from token_world import BaseClass
from token_world import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m token_world
#or
$ token_world
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Acknowledgements

Very loosely inspired by:

Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology, 2:1–2:22. https://doi.org/10.1145/3586183.3606763
