# Customization Guide

Token World is designed to be highly flexible, allowing you to create unique simulations tailored to your needs. This guide explains how to customize agents, entities, and global settings to build your ideal simulation.

---
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**
## Customizing Agents

Agents are the core of Token World, driving interactions within the environment. You can define agents in the configuration file.

### Adding a New Agent

To add a new agent, ask the environment agent. Each agent requires:
- **Name**: A unique identifier for the agent.
- **Role**: The agent’s role in the simulation.
- **Personality**: A prompt describing the agent's behavior and goals.

---

## Customizing Entities

Entities are objects in the environment that agents interact with. You can define entities with properties that govern their behavior.

### Adding a New Entity

To add entities, ask the environment agent. Each entity requires:
- **Name**: A unique identifier.
- **Properties**: Key-value pairs defining its attributes.

Example:
```json
{
    "name": "Apple",
    "properties": {
        "isEdible": true,
        "calories": 50
    }
}
```
```json
{
    "name": "Tree",
    "properties": {
        "canGrowFruit": true,
        "height": 5
    }
}
```

---

## Customizing Global Settings

Global settings define the overall simulation parameters, such as:
- **Time Steps**: Number of iterations for the simulation.
- **Logging Level**: Verbosity of simulation output.
- **Debug Mode**: Whether debugging tools are active.

### Editing Global Settings

Modify the `<missing documentation>` file to adjust these parameters. Example:
```json
"settings": {
  "timeSteps": 100,
  "loggingLevel": "verbose",
  "debugMode": true
}
```

---

## Extending Functionality
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**
For advanced customization, you can:
1. Add new actions or behaviors in the `src/actions` folder.
2. Define new grounding mechanisms in the `src/grounding` module.
3. Create new debugging features in the `web/` directory.

---

## Next Steps

Once you've customized your agents and entities, explore the [Examples](examples/small_town.md) section to see how these customizations can bring your scenarios to life!
