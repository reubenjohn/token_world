# Example: Small Town Simulation

This example demonstrates how to set up and run a small-town simulation in Token World. The scenario involves a community of agents interacting with each other and their environment, creating emergent behaviors over time.

---
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**

## Scenario Overview

The small town includes:
- **Agents**: A mix of professions, each with distinct roles and personalities.
- **Entities**: Objects and features in the town, such as food items, tools, and buildings.
- **Interactions**: Agents perform tasks like trading, farming, or exploring, dynamically changing the environment.

---

## Configuration

Below is the configuration for a small-town simulation:

### Agents

Define the town's residents:
```json
"agents": [
  {
    "name": "Alice",
    "role": "Farmer",
    "personality": "Curious and resourceful. Enjoys growing crops and helping others."
  },
  {
    "name": "Bob",
    "role": "Merchant",
    "personality": "Clever and opportunistic. Seeks opportunities for trade and negotiation."
  },
  {
    "name": "Eve",
    "role": "Explorer",
    "personality": "Adventurous and brave. Likes to discover new areas and gather resources."
  }
]
```

### Entities

Define the resources available in the town:
```json
"entities": [
  {
    "name": "Apple",
    "properties": {
      "isEdible": true,
      "calories": 50
    }
  },
  {
    "name": "Plow",
    "properties": {
      "isTool": true,
      "durability": 100
    }
  },
  {
    "name": "Field",
    "properties": {
      "canGrowCrops": true,
      "size": 10
    }
  }
]
```

---

## Running the Simulation

1. Use the provided configuration files (`scenario.json` and `entities.json`).
2. Start the simulation:
   ```bash
   python run_simulation.py
   ```
3. Observe agent actions and state changes in real time.

---

## Example Interactions

As the simulation progresses, you might see logs like:
```text
[Agent: Alice] Action: "Plant crops in the field."
[Environment] Preconditions met. Action executed.
[Entity: Field] Crops planted. Growth started.

[Agent: Bob] Action: "Trade apples with Alice."
[Environment] Preconditions met. Trade executed.
[Agent: Alice] Received coins.
[Agent: Bob] Received apples.

[Agent: Eve] Action: "Explore the forest."
[Environment] Preconditions met. New area discovered. Resources added: [Wood].
```

---

## Experimentation Ideas

1. **Add More Agents**: Introduce new roles like a blacksmith or healer.
2. **Modify Entities**: Add new tools or resources, such as gold or wheat.
3. **Tune Personalities**: Change agents’ personalities to see how their behaviors evolve.

---

## Next Steps

Expand this small-town simulation or try a different scenario, like a [Role-Playing Game](role_playing.md), to explore Token World's full potential!

