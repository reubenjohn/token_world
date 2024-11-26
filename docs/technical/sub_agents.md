# Sub-environment Delegation

Token World employs specialized sub-environments to handle specific types of actions, ensuring that complex interactions are processed efficiently and logically. This section details how sub-environment delegation works, the types of sub-environments available, and how you can extend or customize them.

---

## What Are Sub-environments?

Sub-environments are specialized modules designed to:
1. Process specific categories of actions (e.g., navigation, crafting, trading).
2. Ensure efficient handling of tasks by delegating responsibilities.
3. Provide fallback mechanisms for unsupported or failed actions.

---

## Workflow: Sub-environment Delegation

1. **Action Identification**  
   - An agent generates an action (e.g., *"Trade apples with Bob."*).
   - The environment identifies the action type and delegates it to the appropriate sub-environment.

2. **Sub-environment Processing**  
   - The sub-environment validates the action’s feasibility (e.g., checks if Bob has apples to trade).
   - Executes the action and applies its effects to the entities involved.

3. **Fallback Mechanisms**  
   - If a sub-environment cannot process the action, it either:
     - Marks the action as failed, or
     - Provides feedback to the main agent for adjustment.

---

## Types of Sub-environments

### 1. Navigation Sub-environment
- Handles actions related to movement and exploration.
- Examples:
  - *"Move to the forest."*
  - *"Explore the cave."*

### 2. Crafting Sub-environment
- Processes crafting-related actions.
- Examples:
  - *"Craft a sword using iron and wood."*
  - *"Repair the plow."*

### 3. Trading Sub-environment
- Manages trade and barter actions between agents.
- Examples:
  - *"Trade apples with Bob for coins."*
  - *"Sell iron ore to the blacksmith."*

### 4. Combat Sub-environment
- Handles combat-related interactions.
- Examples:
  - *"Attack the goblin with a sword."*
  - *"Defend against the dragon’s fire breath."*

---

## Error Handling

1. **Unsupported Actions**  
   - If no sub-environment can process the action, it is marked as unsupported.
   - Feedback is logged for debugging.

2. **Failed Preconditions**  
   - Sub-environments log detailed errors when preconditions for actions are not met.

---

## Use Cases for Sub-environments

1. **Modular Design**: Separate concerns for different action types.
2. **Complex Scenarios**: Handle intricate interactions like multi-step quests.
3. **Extensibility**: Easily add or modify sub-environments to introduce new behaviors.

---

## Next Steps

To learn more about how sub-environments interact with the environment and main agents, explore:  
- [Environment Design](environment.md)  
- [Action Validation](action_validation.md)
