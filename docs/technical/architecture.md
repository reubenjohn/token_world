# Architecture Overview

Token World is designed with modularity, scalability, and flexibility in mind. This section provides an in-depth look at the framework's architecture, including its core components and how they interact.

---

## Core Components

1. **Agents**  
   - Represent autonomous entities in the simulation.
   - Defined by their **roles**, **personalities**, and **abilities**.
   - Generate natural language actions that interact with the environment.

2. **Environment**  
   - The simulation’s central system, managing entities and grounding agent actions.
   - Handles preconditions, effects, and updates for all interactions.
   - Dynamically adapts as new mechanics are generated during the simulation.

3. **Entities**  
   - Represent objects, resources, and structures in the simulation.
   - Stored in an SQLite database for efficient querying and state management.
   - Defined by unique properties and attributes.

4. **Grounding Mechanisms**  
   - Validate agent actions by checking preconditions and applying effects.
   - Ensure logical consistency and prevent hallucinations.
   - Dynamically generate new mechanics as needed.

5. **Debugging Tool**  
   - Provides a real-time interface for observing agent interactions and entity states.
   - Designed to help troubleshoot and analyze complex scenarios.

---

## System Workflow

1. **Agent Action Generation**  
   - Agents use large language models (LLMs) to generate natural language actions.
   - Example: *"Plant crops in the field."*

2. **Action Validation**  
   - The environment validates the action using grounding mechanisms:
     - Checks preconditions (e.g., field must be empty).
     - Applies effects (e.g., crops are planted, field state updated).

3. **State Updates**  
   - Entities are updated based on the action's effects.
   - Example: Field’s status changes to *"planted,"* and crops are added as new entities.

4. **Dynamic Evolution**  
   - New mechanics are generated on demand.
   - Example: If agents discover a forest, new interactions like *"chop wood"* become available.

5. **Logging and Visualization**  
   - All interactions and state changes are logged.
   - The debugging tool provides a graphical interface for real-time analysis.

---

## Modular Design

Token World is built with modularity to enable easy extension and customization:

- **Agents Module**: Define agent roles, behaviors, and actions.
- **Environment Module**: Manages entities, actions, and mechanics.
- **Grounding Module**: Validates and executes actions.
- **Web Interface**: Debugging tool built using Flask for visualization.

---

## Scalability

1. **Local Simulations**: Optimized for small to medium-scale simulations on personal laptops.
2. **Distributed Systems**: Can be extended for larger simulations using distributed architectures.
3. **Model Flexibility**: Supports lightweight LLMs for efficiency, with the option to integrate more powerful models as needed.

---

## Diagram: System Architecture

(Include a simple diagram showing the flow of data between agents, the environment, entities, and grounding mechanisms.)

---

## Next Steps

Explore specific technical details:
- [Action Validation](action_validation.md)
- [Environment Design](environment.md)
- [Sub-Agent Delegation](sub_agents.md)
