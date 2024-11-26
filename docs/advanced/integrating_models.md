# Integrating New Models

Token World is designed to be compatible with a variety of large language models (LLMs). This guide explains how to integrate custom or third-party models to enhance agent behavior and expand simulation capabilities.

---
> **WARNING: The below steps are for illustrative purposes only and not meant to serve as actual instructions**

## Supported Model Types

1. **Pre-Trained Models**  
   - Popular LLMs like GPT, LLaMA, and OpenAI’s GPT-3.5/4.
2. **Fine-Tuned Models**  
   - Custom models adapted for specific use cases, such as domain-specific interactions.
3. **Local Lightweight Models**  
   - Optimized models for resource-constrained environments (e.g., 2-8 billion parameters).

---

## Integration Steps

### 1. Select Your Model
- Choose a model based on your needs and hardware:
  - **OpenAI API**: For GPT models via API calls.
  - **Hugging Face Transformers**: For local or custom models.
  - **Custom APIs**: For proprietary or self-hosted models.

### 2. Update the Configuration
Modify the `config/settings.json` file to specify your model:
```json
"settings": {
  "modelType": "huggingface",
  "modelPath": "gpt-neo-2.7b",
  "useGPU": true
}
```

### 3. Install Necessary Libraries
Install the libraries required for your chosen model:
- **Hugging Face Transformers**:
  ```bash
  pip install transformers
  ```
- **OpenAI API**:
  ```bash
  pip install openai
  ```

### 4. Update the Model Handler
Extend the `src/models/model_handler.py` file to include your model’s initialization and query logic:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

class HuggingFaceModel:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
    
    def generate_response(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs["input_ids"])
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 5. Test the Integration
Run a simple simulation to ensure the model responds correctly:
```bash
python run_simulation.py --test-model
```

---

## Advanced Configuration

### Enable Multiple Models
Token World supports multiple models for different agents:
```json
"agents": [
  {
    "name": "Alice",
    "model": "gpt-3.5"
  },
  {
    "name": "Bob",
    "model": "gpt-neo-2.7b"
  }
]
```

### Add Custom Prompts
Customize agent prompts in the `agents.json` file:
```json
"agents": [
  {
    "name": "Alice",
    "prompt": "You are a farmer in a small town. Respond with curiosity."
  }
]
```

---

## Optimization Tips

1. **Use Quantized Models**  
   Reduce resource usage by using quantized weights for local models.
   ```bash
   pip install optimum
   ```
   Example:
   ```python
   from optimum.onnxruntime import ORTModelForCausalLM
   model = ORTModelForCausalLM.from_pretrained("quantized-model")
   ```

2. **Batch Inference**  
   Process multiple agent prompts in a single batch to improve efficiency.

3. **Fallback Models**  
   Use lightweight models as fallbacks if the primary model exceeds resource limits.

---

## Example: Integrating a Custom Model

### Scenario
Integrate a fine-tuned model trained for customer service simulations.

### Steps
1. Train the model using domain-specific data.
2. Add the model to the `config/settings.json` file:
   ```json
   "settings": {
       "modelType": "huggingface",
       "modelPath": "custom-service-model"
   }
   ```
3. Update prompts to reflect the new domain:
   ```json
   "agents": [
       {
           "name": "SupportBot",
           "prompt": "You are a helpful customer service representative."
       }
   ]
   ```

---

## Next Steps

To further customize agent behavior, explore:
- [Agent Evolution](agent_evolution.md)  
- [Sub-Agent Delegation](../technical/sub_agents.md)
