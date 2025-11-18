# Language Models

Model integration layer supporting Google Gemini and other LLM providers with a unified interface and model registry for management.

## Capabilities

### Base LLM Classes

Core classes for LLM integration and model management.

```python { .api }
class BaseLlm:
    """Base class for LLM implementations."""
    
    def __init__(self, model_name: str, **kwargs):
        """
        Initialize base LLM.
        
        Args:
            model_name (str): Name/identifier of the model
            **kwargs: Model-specific configuration parameters
        """
        pass
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text response from the model.
        
        Args:
            prompt (str): Input prompt
            **kwargs: Generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: Generated response
        """
        pass
    
    def generate_async(self, prompt: str, **kwargs):
        """
        Generate text response asynchronously.
        
        Args:
            prompt (str): Input prompt
            **kwargs: Generation parameters
            
        Returns:
            Coroutine: Async generated response
        """
        pass

class Gemini(BaseLlm):
    """Google Gemini LLM implementation."""
    
    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        api_key: str = None,
        project_id: str = None,
        location: str = "us-central1",
        **kwargs
    ):
        """
        Initialize Gemini model.
        
        Args:
            model_name (str): Gemini model variant
            api_key (str, optional): Google API key
            project_id (str, optional): Google Cloud project ID
            location (str): Model location/region
            **kwargs: Additional Gemini-specific parameters
        """
        pass
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.95,
        top_k: int = 40,
        **kwargs
    ) -> str:
        """
        Generate response using Gemini.
        
        Args:
            prompt (str): Input prompt
            temperature (float): Sampling temperature (0.0-1.0)
            max_tokens (int): Maximum tokens to generate
            top_p (float): Top-p sampling parameter
            top_k (int): Top-k sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated response
        """
        pass

class LLMRegistry:
    """Registry for LLM model management."""
    
    def __init__(self):
        """Initialize the LLM registry."""
        pass
    
    def register(self, name: str, llm_class: type, **default_kwargs):
        """
        Register an LLM class in the registry.
        
        Args:
            name (str): Registry name for the LLM
            llm_class (type): LLM class to register
            **default_kwargs: Default parameters for the LLM
        """
        pass
    
    def get(self, name: str, **kwargs) -> BaseLlm:
        """
        Get an LLM instance from the registry.
        
        Args:
            name (str): Registry name of the LLM
            **kwargs: Override parameters for the LLM
            
        Returns:
            BaseLlm: LLM instance
        """
        pass
    
    def list_models(self) -> list:
        """
        List all registered models.
        
        Returns:
            list: List of registered model names
        """
        pass
```

## Usage Examples

### Using Gemini Models

```python
from google.adk.models import Gemini

# Initialize Gemini with default settings
gemini = Gemini(model_name="gemini-2.0-flash")

# Generate a response
response = gemini.generate(
    prompt="Explain quantum computing in simple terms",
    temperature=0.7,
    max_tokens=500
)
print(response)

# Generate with specific parameters
creative_response = gemini.generate(
    prompt="Write a creative story about AI",
    temperature=0.9,  # More creative
    max_tokens=1000
)
```

### Custom Model Configuration

```python
from google.adk.models import Gemini

# Configure Gemini with specific settings
gemini = Gemini(
    model_name="gemini-2.0-flash",
    project_id="my-project",
    location="us-west1",
    api_key="your-api-key"
)

# Use with custom generation parameters
response = gemini.generate(
    prompt="Analyze this data...",
    temperature=0.3,  # More deterministic
    top_p=0.8,
    top_k=20
)
```

### Using with Agents

```python
from google.adk.agents import Agent
from google.adk.models import Gemini

# Create model instance
model = Gemini(
    model_name="gemini-2.0-flash",
    temperature=0.7
)

# Use model with agent
agent = Agent(
    name="analysis_agent",
    model=model,  # Pass model instance
    instruction="Analyze data and provide insights"
)

# Or use model name directly (ADK will create the instance)
agent = Agent(
    name="simple_agent",
    model="gemini-2.0-flash",  # Model string
    instruction="Help with general tasks"
)
```

### Async Model Usage

```python
import asyncio
from google.adk.models import Gemini

async def async_generation():
    gemini = Gemini()
    
    # Generate response asynchronously
    response = await gemini.generate_async(
        prompt="What are the benefits of async programming?",
        temperature=0.5
    )
    
    return response

# Run async generation
response = asyncio.run(async_generation())
print(response)
```

### Model Registry

```python
from google.adk.models import LLMRegistry, Gemini, BaseLlm

# Create registry
registry = LLMRegistry()

# Register Gemini models with different configurations
registry.register(
    "gemini-creative",
    Gemini,
    model_name="gemini-2.0-flash",
    temperature=0.9,
    top_p=0.95
)

registry.register(
    "gemini-analytical",
    Gemini,
    model_name="gemini-2.0-flash",
    temperature=0.3,
    top_p=0.8
)

# Get models from registry
creative_model = registry.get("gemini-creative")
analytical_model = registry.get("gemini-analytical")

# Override registry defaults
custom_model = registry.get("gemini-creative", temperature=0.5)
```

### Custom LLM Implementation

```python
from google.adk.models import BaseLlm

class CustomLLM(BaseLlm):
    def __init__(self, api_endpoint: str, **kwargs):
        super().__init__(**kwargs)
        self.api_endpoint = api_endpoint
    
    def generate(self, prompt: str, **kwargs) -> str:
        # Custom implementation for your LLM provider
        # Make API call to your endpoint
        return "Custom LLM response"
    
    async def generate_async(self, prompt: str, **kwargs):
        # Async implementation
        return "Async custom LLM response"

# Use custom LLM
custom_llm = CustomLLM(
    model_name="custom-model-v1",
    api_endpoint="https://api.custom-llm.com"
)

# Register in registry
registry = LLMRegistry()
registry.register("custom", CustomLLM, api_endpoint="https://api.custom-llm.com")
```

### Model Comparison

```python
from google.adk.models import Gemini

# Create different model configurations
models = {
    "conservative": Gemini(temperature=0.1),
    "balanced": Gemini(temperature=0.5),
    "creative": Gemini(temperature=0.9)
}

prompt = "Describe the future of AI"

# Compare responses
for name, model in models.items():
    response = model.generate(prompt, max_tokens=200)
    print(f"{name.upper()} Model Response:")
    print(response)
    print("-" * 50)
```

### Batch Processing

```python
from google.adk.models import Gemini

gemini = Gemini()

prompts = [
    "Summarize the history of computing",
    "Explain machine learning basics",
    "Describe renewable energy types"
]

# Process multiple prompts
responses = []
for prompt in prompts:
    response = gemini.generate(prompt, max_tokens=300)
    responses.append(response)

# Or async batch processing
async def batch_generate(prompts):
    tasks = [gemini.generate_async(prompt) for prompt in prompts]
    return await asyncio.gather(*tasks)

# responses = asyncio.run(batch_generate(prompts))
```