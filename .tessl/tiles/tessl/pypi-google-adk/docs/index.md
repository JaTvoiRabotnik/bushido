# Google Agent Development Kit (ADK)

A comprehensive Python framework designed for building, evaluating, and deploying sophisticated AI agents with maximum flexibility and control. This code-first toolkit provides developers with a rich ecosystem of pre-built tools, seamless integration with the Google ecosystem (particularly Gemini models), and the ability to create modular multi-agent systems that can be deployed anywhere from Cloud Run to Vertex AI Agent Engine.

## Package Information

- **Package Name**: google-adk
- **Language**: Python 3.9+
- **Installation**: `pip install google-adk`
- **License**: Apache 2.0
- **Documentation**: https://google.github.io/adk-docs/

## Core Imports

```python
import google.adk
from google.adk import Agent, Runner
```

For agents and execution:

```python
from google.adk.agents import Agent, LlmAgent, BaseAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner, InMemoryRunner
```

For tools:

```python
from google.adk.tools import BaseTool, FunctionTool, google_search, enterprise_web_search
```

## Basic Usage

### Single Agent

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

# Create a simple search assistant
agent = Agent(
    name="search_assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search]
)

# Run the agent using InMemoryRunner (recommended for simple usage)
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent)
user_message = types.Content(parts=[types.Part(text="What's the weather like today?")])

# Execute and get events
for event in runner.run(
    user_id="user123",
    session_id="session456", 
    new_message=user_message
):
    if event.content:
        print(event.content)
```

### Multi-Agent System

```python
from google.adk.agents import LlmAgent

# Define individual agents
greeter = LlmAgent(
    name="greeter", 
    model="gemini-2.0-flash",
    instruction="Greet users warmly and professionally."
)

task_executor = LlmAgent(
    name="task_executor", 
    model="gemini-2.0-flash",
    instruction="Execute tasks efficiently and provide detailed results."
)

# Create coordinator agent with sub-agents
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    description="I coordinate greetings and tasks.",
    sub_agents=[greeter, task_executor]
)

# Run the multi-agent system using InMemoryRunner
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(coordinator)
user_message = types.Content(parts=[types.Part(text="Hello, can you help me with a task?")])

# Execute and get events
for event in runner.run(
    user_id="user123",
    session_id="session456",
    new_message=user_message
):
    if event.content:
        print(event.content)
```

## Architecture

The ADK follows a modular, hierarchical architecture:

- **Agents**: Core agent classes (BaseAgent, LlmAgent, specialized agents)
- **Runners**: Execution engines for synchronous, asynchronous, and live execution
- **Tools**: Extensible tool framework for agent capabilities
- **Models**: LLM integration layer supporting Gemini and other models
- **Services**: Infrastructure for memory, sessions, artifacts, and authentication
- **Plugins**: Extensible plugin system for custom functionality

## Capabilities

### Agent Framework

Core agent classes and configuration for building single agents and multi-agent systems, supporting various execution patterns and orchestration strategies.

```python { .api }
class Agent: ...  # Main agent class (alias for LlmAgent)
class BaseAgent: ...  # Abstract base class for all agents
class LlmAgent: ...  # LLM-based agent implementation
class LoopAgent: ...  # Agent that executes in a loop
class ParallelAgent: ...  # Agent for parallel task execution
class SequentialAgent: ...  # Agent for sequential task execution
```

[Agent Framework](./agents.md)

### Execution Engine

Runners provide the execution environment for agents, supporting synchronous, asynchronous, and streaming execution modes with resource management and cleanup.

```python { .api }
class Runner:
    def __init__(
        self,
        *,
        app_name: str,
        agent: BaseAgent,
        plugins: Optional[List[BasePlugin]] = None,
        artifact_service: Optional[BaseArtifactService] = None,
        session_service: BaseSessionService,
        memory_service: Optional[BaseMemoryService] = None,
        credential_service: Optional[BaseCredentialService] = None,
    ): ...
    
    def run(
        self,
        *,
        user_id: str,
        session_id: str,
        new_message: types.Content,
        run_config: RunConfig = RunConfig(),
    ) -> Generator[Event, None, None]: ...
    
    async def run_async(
        self,
        *,
        user_id: str,
        session_id: str,
        new_message: types.Content,
        state_delta: Optional[dict[str, Any]] = None,
        run_config: RunConfig = RunConfig(),
    ) -> AsyncGenerator[Event, None]: ...
    
    async def run_live(
        self,
        *,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        live_request_queue: LiveRequestQueue,
        run_config: RunConfig = RunConfig(),
        session: Optional[Session] = None,
    ) -> AsyncGenerator[Event, None]: ...
    
    async def close(self): ...

class InMemoryRunner(Runner):
    def __init__(
        self,
        agent: BaseAgent,
        *,
        app_name: str = 'InMemoryRunner',
        plugins: Optional[list[BasePlugin]] = None,
    ): ...
```

[Execution Engine](./runners.md)

### Tools Framework

Comprehensive tool ecosystem including built-in tools, custom function wrappers, and specialized toolsets for Google Cloud services, databases, and APIs.

```python { .api }
class BaseTool: ...  # Base class for all tools
class FunctionTool: ...  # Tool wrapper for Python functions
class LongRunningFunctionTool: ...  # Tool for long-running operations
class AgentTool: ...  # Tool for agent interactions

# Built-in tool functions
def google_search(query: str, **kwargs): ...
def enterprise_web_search(query: str, **kwargs): ...
def url_context(url: str): ...
def get_user_choice(choices: list, prompt: str = None): ...
```

[Tools Framework](./tools.md)

### Language Models

Model integration layer supporting Google Gemini and other LLM providers with a unified interface and model registry for management.

```python { .api }
class BaseLlm: ...  # Base class for LLM implementations
class Gemini: ...  # Google Gemini LLM implementation
class LLMRegistry: ...  # Registry for LLM model management
```

[Language Models](./models.md)

### Google Cloud Integration

Specialized toolsets for Google Cloud services including BigQuery, Bigtable, Spanner, and Google APIs (Calendar, Gmail, Sheets, Docs, YouTube).

```python { .api }
class BigQueryToolset: ...  # BigQuery database interaction
class BigtableToolset: ...  # Bigtable interaction toolset
class SpannerToolset: ...  # Spanner database interaction
class GoogleApiToolset: ...  # Generic Google API toolset
class CalendarToolset: ...  # Google Calendar integration
class GmailToolset: ...  # Gmail integration
```

[Google Cloud Integration](./google-cloud.md)

### Memory and Session Management

Infrastructure services for persistent memory, session state, and artifact storage with support for in-memory and cloud-based implementations.

```python { .api }
class BaseMemoryService: ...  # Base class for memory services
class InMemoryMemoryService: ...  # In-memory memory implementation
class VertexAiMemoryBankService: ...  # Vertex AI memory bank service

class BaseSessionService: ...  # Base class for session services
class InMemorySessionService: ...  # In-memory session implementation
class VertexAiSessionService: ...  # Vertex AI session service
```

[Memory and Sessions](./memory-sessions.md)

### Authentication and Security

Authentication framework supporting OAuth2, OpenID Connect, and Google Cloud authentication with configurable schemes and credential management.

```python { .api }
class AuthCredential: ...  # Authentication credential object
class OAuth2Auth: ...  # OAuth2 authentication
class OpenIdConnectWithConfig: ...  # OpenID Connect authentication
class AuthHandler: ...  # Authentication handler
class AuthConfig: ...  # Authentication configuration
```

[Authentication](./authentication.md)

### Code Execution

Code execution framework supporting built-in, local, container-based, and Vertex AI code execution environments with safety controls.

```python { .api }
class BaseCodeExecutor: ...  # Base class for code executors
class BuiltInCodeExecutor: ...  # Built-in code executor
class UnsafeLocalCodeExecutor: ...  # Local code executor (unsafe)
class VertexAiCodeExecutor: ...  # Vertex AI code executor
class ContainerCodeExecutor: ...  # Container-based code executor
```

[Code Execution](./code-execution.md)

### Advanced Features

Planning, evaluation, event system, and plugin framework for sophisticated agent behaviors and custom extensions.

```python { .api }
class BasePlanner: ...  # Base class for planners
class BuiltInPlanner: ...  # Built-in planner implementation
class AgentEvaluator: ...  # Agent evaluation framework
class Event: ...  # Event object for agent communication
class BasePlugin: ...  # Base class for plugins
```

[Advanced Features](./advanced.md)

## Types

```python { .api }
# Core execution types
class InvocationContext:
    """Context passed during agent invocation."""
    pass

class RunConfig:
    """Configuration for agent execution."""
    pass

class Event:
    """Event object for agent communication and results."""
    pass

# Tool and context types
class ToolContext:
    """Context passed to tools during execution."""
    pass

# Live streaming types  
class LiveRequest:
    """Live request object for streaming."""
    pass

class LiveRequestQueue:
    """Queue for managing live requests."""
    pass

# Session and memory types
class Session:
    """Session object for conversation state."""
    pass

# Service interfaces
class BaseAgent:
    """Abstract base class for all agents."""
    pass

class BasePlugin:
    """Base class for plugins."""
    pass

class BaseArtifactService:
    """Base class for artifact services."""
    pass

class BaseSessionService:
    """Base class for session services."""
    pass

class BaseMemoryService:
    """Base class for memory services."""
    pass

class BaseCredentialService:
    """Base class for credential services."""
    pass

# External types (from google.genai)
from google.genai import types  # Content, Part, etc.
from typing import Generator, AsyncGenerator, Optional, List, Any
```