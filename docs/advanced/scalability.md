# Scalability

Token World is designed to accommodate simulations of varying complexity, from small-scale experiments on personal devices to large-scale simulations on distributed systems. This section explains how to optimize and scale your simulations effectively.

---

## Levels of Scalability

### 1. Small-Scale Simulations
- **Use Case**: Simple setups with a limited number of agents and entities.
- **Environment**: Personal laptops or low-power machines.
- **Optimization Tips**:
  - Use lightweight LLMs for agent processing (e.g., models with 2-8 billion parameters).
  - Limit the number of agents and entities to reduce computational overhead.
  - Adjust simulation time steps to a manageable number in `config/settings.json`.

### 2. Medium-Scale Simulations
- **Use Case**: More complex scenarios with diverse agent interactions and moderate computational demands.
- **Environment**: High-performance local machines or basic cloud instances.
- **Optimization Tips**:
  - Leverage GPU acceleration for LLM inference.
  - Use database indexing for faster querying of entities.
  - Implement periodic data cleanup to manage memory usage.

### 3. Large-Scale Simulations
- **Use Case**: Advanced research or commercial applications with numerous agents, entities, and interactions.
- **Environment**: Distributed systems or high-powered cloud environments.
- **Optimization Tips**:
  - Distribute agent processing across multiple nodes.
  - Use efficient communication protocols (e.g., gRPC) between nodes.
  - Enable batch processing for actions to minimize overhead.

---

## Techniques for Optimization

### 1. Lightweight Models
- Use models optimized for inference on resource-constrained systems, such as [Hugging Face Transformers](https://huggingface.co/transformers/) with quantized weights.

### 2. Entity Partitioning
- Divide the environment into regions or zones, each managed independently.
- Example:
  - Agents in "Town" only interact with entities in that region.
  - Other regions, like "Forest," are activated only when agents explore them.

### 3. Action Prioritization
- Assign priority levels to agent actions to process critical tasks first.
- Example:
  - High priority: Actions affecting global states (e.g., "Build a bridge").
  - Low priority: Routine actions (e.g., "Collect apples").

### 4. Dynamic Resource Allocation
- Dynamically allocate system resources based on simulation demand.
- Example:
  - Increase memory usage for entity-heavy phases.
  - Optimize CPU usage during action validation.

---

## Distributed Systems

For large-scale simulations, consider a distributed architecture:
1. **Agent Distribution**:
   - Assign a subset of agents to each node for processing.
2. **Entity Synchronization**:
   - Use a centralized database or synchronization protocol to manage global entity states.
3. **Load Balancing**:
   - Implement load balancers to distribute computational tasks evenly.

---

## Example: Scaling a Medium-Sized Simulation

### Configuration
- **Agents**: 50
- **Entities**: 200
- **Hardware**: Local machine with a GPU (e.g., NVIDIA RTX 3080).

### Optimization Steps
1. Use an 8-billion parameter LLM with quantized weights for faster inference.
2. Limit simulation time steps to 500.
3. Enable GPU acceleration for agent processing.

---

## Next Steps

To explore how scalability integrates with other advanced features, see:  
- [Agent Evolution](agent_evolution.md)  
- [Integrating New Models](integrating_models.md)
