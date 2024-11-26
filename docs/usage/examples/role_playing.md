# Example: Role-Playing Game (RPG) Simulation

This example demonstrates how to set up a role-playing game (RPG) scenario in Token World. The RPG simulation involves agents with specific quests, abilities, and interactions in a richly defined environment.

---
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**

## Scenario Overview

The RPG simulation includes:
- **Agents**: Heroes with distinct classes, abilities, and personalities.
- **Entities**: Items, treasures, NPCs, and obstacles.
- **Interactions**: Quest completion, combat, trading, and exploration.

---

## Configuration

Below is the configuration for an RPG simulation:

### Agents

Define the heroes in the RPG world:
```json
"agents": [
  {
    "name": "Thorin",
    "role": "Warrior",
    "personality": "Brave and loyal. Fights for honor and justice.",
    "abilities": {
      "strength": 10,
      "defense": 8
    }
  },
  {
    "name": "Lyra",
    "role": "Mage",
    "personality": "Wise and curious. Excels at casting powerful spells.",
    "abilities": {
      "intelligence": 10,
      "mana": 12
    }
  },
  {
    "name": "Rowan",
    "role": "Rogue",
    "personality": "Sneaky and resourceful. Skilled in stealth and agility.",
    "abilities": {
      "dexterity": 10,
      "stealth": 12
    }
  }
]
```

### Entities

Define the items and objects in the RPG world:
```json
"entities": [
  {
    "name": "Health Potion",
    "properties": {
      "isConsumable": true,
      "healingValue": 20
    }
  },
  {
    "name": "Treasure Chest",
    "properties": {
      "isLootable": true,
      "contents": ["Gold", "Gemstones"]
    }
  },
  {
    "name": "Goblin",
    "properties": {
      "isEnemy": true,
      "strength": 5,
      "health": 30
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
3. Observe the gameplay as agents complete quests and interact with the world.

---

## Example Interactions

As the simulation progresses, you might see logs like:
```text
[Agent: Thorin] Action: "Attack Goblin with sword."
[Environment] Preconditions met. Action executed.
[Entity: Goblin] Health reduced by 10. Current health: 20.

[Agent: Lyra] Action: "Cast fireball spell at Goblin."
[Environment] Preconditions met. Action executed.
[Entity: Goblin] Health reduced by 15. Current health: 5.

[Agent: Rowan] Action: "Loot Treasure Chest."
[Environment] Preconditions met. Contents obtained: [Gold, Gemstones].
```

---

## Experimentation Ideas

1. **Add New Quests**: Introduce multi-step objectives for agents to complete.
2. **Expand Abilities**: Add new skills, such as healing or crafting.
3. **Create Complex Environments**: Define dungeons, forests, or towns with unique interactions.

---

## Next Steps

Once you've explored the RPG simulation, try creating your own custom scenarios or move on to [Experimental Scenarios](experimental.md) for more advanced setups.
