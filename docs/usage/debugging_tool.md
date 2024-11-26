# Debugging Tool

Token World includes a web-based debugging tool to help you visualize and analyze agent interactions, entity states, and simulation progress in real time. This tool is designed to provide transparency and facilitate troubleshooting for complex simulations.

---

## Features

The debugging tool offers:
1. **Real-Time Interaction Logs**:
   - Monitor actions performed by agents and their outcomes.
   - View precondition checks and state changes for each interaction.

2. **Entity State Viewer**:
   - Inspect properties of all entities in the environment.
   - Track dynamic updates to entity states during the simulation.

3. **Visualization Dashboard**:
   - Display the simulation environment graphically (if configured).
   - Show relationships and dependencies between agents and entities.

4. **Error Reporting**:
   - Highlight failed actions and their causes.
   - Provide suggestions for resolving common issues.

---

## Launching the Debugging Tool
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**

1. Ensure you have Flask and Flask-SocketIO installed:
   ```bash
   pip install flask flask-socketio
   ```

2. Start the debugging tool server:
   ```bash
   python run_web_debugger.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

---

## Using the Debugging Tool

### Navigation

The tool provides a simple interface with the following sections:
- **Home**: Overview of the simulation status.
- **Agents**: List of all agents, their actions, and current states.
- **Entities**: Properties and states of all entities in the environment.
- **Logs**: Chronological list of interactions, errors, and events.

### Example Workflow

1. Start your simulation:
   ```bash
   <Missing documentation>
   ```
2. Open the debugging tool in your browser.
3. Monitor actions in the **Logs** tab to verify that agents are performing as expected.
4. Use the **Entities** tab to inspect properties like resource quantities or tool durability.
5. Check the **Agents** tab to view agent-specific stats and behaviors.

---

## Debugging Tips

- **Failed Actions**:
  - Review the preconditions for the failed action in the logs.
  - Verify that the referenced entities exist and meet the required criteria.

- **Unexpected Behaviors**:
  - Use the state viewer to confirm entity properties.
  - Ensure that agent prompts and roles align with expected behaviors.

- **Simulation Stalls**:
  - Check for cyclic dependencies or insufficient resources in the environment.

---

## Next Steps

Once you’ve resolved issues using the debugging tool, explore advanced simulation configurations in the [Customization Guide](customization.md) or dive into [Examples](examples/small_town.md) to see the tool in action.
