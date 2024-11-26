# Example: Experimental Scenarios

This example explores how to create experimental scenarios in **Token World**, ideal for testing agentic workflows, studying emergent behaviors, or conducting academic research. These scenarios push the boundaries of what is possible in multi-agent simulations.

---
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**

## Scenario Overview

Experimental scenarios allow users to:
- Simulate unconventional environments.
- Observe emergent behaviors under specific constraints.
- Test novel mechanics or agent interactions.

Example use cases include:
- Simulating resource competition among agents.
- Exploring social dynamics in constrained environments.
- Testing how agents adapt to evolving scenarios.

---

## Configuration

Below is a sample configuration for an experimental scenario:

### Agents

Define agents with diverse and conflicting goals:
```json
"agents": [
  {
    "name": "Agent A",
    "role": "Resource Collector",
    "personality": "Competitive and focused on maximizing resources.",
    "abilities": {
      "speed": 8,
      "efficiency": 10
    }
  },
  {
    "name": "Agent B",
    "role": "Collaborator",
    "personality": "Team-oriented, prefers working with others to achieve goals.",
    "abilities": {
      "communication": 10,
      "cooperation": 9
    }
  },
  {
    "name": "Agent C",
    "role": "Observer",
    "personality": "Curious and passive, gathers data on other agents' behaviors."
  }
]
```

### Entities

Define experimental resources and environments:
```json
"entities": [
  {
    "name": "Resource Node",
    "properties": {
      "isHarvestable": true,
      "quantity": 100
    }
  },
  {
    "name": "Barrier",
    "properties": {
      "isObstacle": true,
      "canBeBypassed": false
    }
  }
]
```

### Rules

Add global constraints or rules to shape the experiment:
```json
"rules": {
  "maxTimeSteps": 50,
  "resourceRegeneration": {
    "enabled": true,
    "rate": 5
  },
  "collaborationBonus": {
    "enabled": true,
    "multiplier": 1.5
  }
}
```

---

## Running the Simulation

1. Use the provided configuration files (`scenario.json`, `entities.json`, and `rules.json`).
2. Start the simulation:
   ```bash
   python run_simulation.py
   ```
3. Monitor agent behaviors and environmental changes.

---

## Example Interactions

As the simulation progresses, you might observe:
```text
[Agent: Agent A] Action: "Harvest resources from Node 1."
[Environment] Preconditions met. Action executed.
[Entity: Resource Node] Quantity reduced by 10.

[Agent: Agent B] Action: "Collaborate with Agent A."
[Environment] Preconditions met. Collaboration bonus applied. Total resources harvested: 15.

[Agent: Agent C] Action: "Observe Agent A and Agent B's interaction."
[Environment] Data logged for analysis.
```

---

## Experimentation Ideas

1. **Dynamic Rules**: Change rules mid-simulation to observe how agents adapt.
2. **Unbalanced Scenarios**: Provide more resources to certain agents to test competitive dynamics.
3. **Environmental Changes**: Introduce new obstacles or opportunities during runtime.

---

## Next Steps

After experimenting with this scenario, consider incorporating advanced features, such as [Scalability](../../advanced/scalability.md) or creating your own experimental setups for unique research goals.
