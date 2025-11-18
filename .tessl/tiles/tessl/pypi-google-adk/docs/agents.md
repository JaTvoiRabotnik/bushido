# Agent Framework

Core agent classes and configuration for building single agents and multi-agent systems, supporting various execution patterns and orchestration strategies.

## Capabilities

### Base Agent Classes

Abstract base classes and core agent implementations that form the foundation of the ADK agent system.

```python { .api }
class BaseAgent:
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, description: str = None, **kwargs):
        """
        Initialize a base agent.
        
        Args:
            name (str): Agent name
            description (str, optional): Agent description
            **kwargs: Additional configuration parameters
        """
        pass
    
    def run(self, input_text: str, context: InvocationContext = None) -> str:
        """
        Execute the agent with given input.
        
        Args:
            input_text (str): Input text for the agent
            context (InvocationContext, optional): Execution context
            
        Returns:
            str: Agent response
        """
        pass

class LlmAgent(BaseAgent):
    """LLM-based agent implementation."""
    
    def __init__(
        self,
        name: str,
        model: str,
        instruction: str = None,
        description: str = None,
        tools: list = None,
        sub_agents: list = None,
        **kwargs
    ):
        """
        Initialize an LLM agent.
        
        Args:
            name (str): Agent name
            model (str): LLM model identifier (e.g., "gemini-2.0-flash")
            instruction (str, optional): System instruction for the agent
            description (str, optional): Agent description
            tools (list, optional): List of tools available to the agent
            sub_agents (list, optional): List of sub-agents for multi-agent systems
            **kwargs: Additional configuration parameters
        """
        pass

# Alias for LlmAgent
Agent = LlmAgent
```

### Specialized Agent Types

Agents designed for specific execution patterns and workflows.

```python { .api }
class LoopAgent(BaseAgent):
    """Agent that executes in a loop."""
    
    def __init__(
        self,
        name: str,
        agent: BaseAgent,
        max_iterations: int = 10,
        **kwargs
    ):
        """
        Initialize a loop agent.
        
        Args:
            name (str): Agent name
            agent (BaseAgent): The agent to execute in a loop
            max_iterations (int): Maximum number of loop iterations
            **kwargs: Additional configuration parameters
        """
        pass

class ParallelAgent(BaseAgent):
    """Agent for parallel task execution."""
    
    def __init__(
        self,
        name: str,
        agents: list,
        **kwargs
    ):
        """
        Initialize a parallel agent.
        
        Args:
            name (str): Agent name
            agents (list): List of agents to execute in parallel
            **kwargs: Additional configuration parameters
        """
        pass

class SequentialAgent(BaseAgent):
    """Agent for sequential task execution."""
    
    def __init__(
        self,
        name: str,
        agents: list,
        **kwargs
    ):
        """
        Initialize a sequential agent.
        
        Args:
            name (str): Agent name
            agents (list): List of agents to execute sequentially
            **kwargs: Additional configuration parameters
        """
        pass
```

### Agent Configuration and Context

Configuration and context classes for agent execution and invocation.

```python { .api }
class InvocationContext:
    """Context passed during agent invocation."""
    
    def __init__(
        self,
        session_id: str = None,
        user_id: str = None,
        metadata: dict = None,
        **kwargs
    ):
        """
        Initialize invocation context.
        
        Args:
            session_id (str, optional): Session identifier
            user_id (str, optional): User identifier
            metadata (dict, optional): Additional context metadata
            **kwargs: Additional context parameters
        """
        pass

class RunConfig:
    """Configuration for agent execution."""
    
    def __init__(
        self,
        max_iterations: int = None,
        timeout: float = None,
        temperature: float = None,
        **kwargs
    ):
        """
        Initialize run configuration.
        
        Args:
            max_iterations (int, optional): Maximum execution iterations
            timeout (float, optional): Execution timeout in seconds
            temperature (float, optional): LLM temperature setting
            **kwargs: Additional configuration parameters
        """
        pass
```

### Live Request Handling

Classes for handling streaming and live agent interactions.

```python { .api }
class LiveRequest:
    """Live request object for streaming."""
    
    def __init__(self, request_data: dict, **kwargs):
        """
        Initialize a live request.
        
        Args:
            request_data (dict): Request data
            **kwargs: Additional request parameters
        """
        pass

class LiveRequestQueue:
    """Queue for managing live requests."""
    
    def __init__(self, max_size: int = None, **kwargs):
        """
        Initialize a live request queue.
        
        Args:
            max_size (int, optional): Maximum queue size
            **kwargs: Additional queue parameters
        """
        pass
    
    def put(self, request: LiveRequest):
        """
        Add a request to the queue.
        
        Args:
            request (LiveRequest): Request to add
        """
        pass
    
    def get(self) -> LiveRequest:
        """
        Get a request from the queue.
        
        Returns:
            LiveRequest: Next request in queue
        """
        pass
```

## Usage Examples

### Creating a Simple Agent

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="research_assistant",
    model="gemini-2.0-flash",
    instruction="You are a research assistant. Use web search to find accurate information.",
    description="An agent that helps with research tasks",
    tools=[google_search]
)
```

### Multi-Agent System

```python
from google.adk.agents import LlmAgent

# Create specialized agents
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.0-flash", 
    instruction="Research topics thoroughly using available tools.",
    tools=[google_search]
)

writer = LlmAgent(
    name="writer",
    model="gemini-2.0-flash",
    instruction="Write clear, well-structured content based on research."
)

# Create coordinator
coordinator = LlmAgent(
    name="content_creator",
    model="gemini-2.0-flash",
    description="Coordinates research and writing to create high-quality content.",
    sub_agents=[researcher, writer]
)
```

### Sequential Workflow

```python
from google.adk.agents import SequentialAgent, LlmAgent

# Create agents for each step
data_collector = LlmAgent(name="collector", model="gemini-2.0-flash", ...)
data_processor = LlmAgent(name="processor", model="gemini-2.0-flash", ...)
report_generator = LlmAgent(name="reporter", model="gemini-2.0-flash", ...)

# Create sequential workflow
workflow = SequentialAgent(
    name="data_analysis_workflow",
    agents=[data_collector, data_processor, report_generator]
)
```

### Loop Agent for Iterative Tasks

```python
from google.adk.agents import LoopAgent, LlmAgent

# Create base agent
iterative_agent = LlmAgent(
    name="problem_solver",
    model="gemini-2.0-flash",
    instruction="Solve problems step by step, refining your approach with each iteration."
)

# Wrap in loop agent
loop_solver = LoopAgent(
    name="iterative_solver",
    agent=iterative_agent,
    max_iterations=5
)
```