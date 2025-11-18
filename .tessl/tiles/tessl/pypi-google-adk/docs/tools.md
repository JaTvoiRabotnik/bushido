# Tools Framework

Comprehensive tool ecosystem including built-in tools, custom function wrappers, and specialized toolsets for Google Cloud services, databases, and APIs.

## Capabilities

### Core Tool Classes

Base classes and implementations for creating and managing tools within the ADK framework.

```python { .api }
class BaseTool:
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str, **kwargs):
        """
        Initialize a base tool.
        
        Args:
            name (str): Tool name
            description (str): Tool description
            **kwargs: Additional tool parameters
        """
        pass
    
    def execute(self, context: ToolContext, **kwargs):
        """
        Execute the tool.
        
        Args:
            context (ToolContext): Tool execution context
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        pass

class FunctionTool(BaseTool):
    """Tool wrapper for Python functions."""
    
    def __init__(self, func: callable, name: str = None, description: str = None, **kwargs):
        """
        Initialize a function tool.
        
        Args:
            func (callable): Python function to wrap
            name (str, optional): Tool name (defaults to function name)
            description (str, optional): Tool description (defaults to function docstring)
            **kwargs: Additional tool parameters
        """
        pass

class LongRunningFunctionTool(BaseTool):
    """Tool for long-running operations."""
    
    def __init__(self, func: callable, timeout: float = None, **kwargs):
        """
        Initialize a long-running function tool.
        
        Args:
            func (callable): Long-running function to wrap
            timeout (float, optional): Execution timeout in seconds
            **kwargs: Additional tool parameters
        """
        pass

class AgentTool(BaseTool):
    """Tool for agent interactions."""
    
    def __init__(self, agent, **kwargs):
        """
        Initialize an agent tool.
        
        Args:
            agent: Agent instance to wrap as a tool
            **kwargs: Additional tool parameters
        """
        pass

class ExampleTool(BaseTool):
    """Example tool implementation for reference."""
    
    def __init__(self, **kwargs):
        """Initialize example tool."""
        pass

class ToolContext:
    """Context passed to tools during execution."""
    
    def __init__(self, session_id: str = None, user_id: str = None, **kwargs):
        """
        Initialize tool context.
        
        Args:
            session_id (str, optional): Session identifier
            user_id (str, optional): User identifier
            **kwargs: Additional context parameters
        """
        pass
```

### Built-in Tool Functions

Pre-built tools for common operations and integrations.

```python { .api }
def google_search(query: str, num_results: int = 10, **kwargs) -> dict:
    """
    Perform Google search and return results.
    
    Args:
        query (str): Search query
        num_results (int): Number of results to return
        **kwargs: Additional search parameters
        
    Returns:
        dict: Search results with titles, URLs, and snippets
    """
    pass

def enterprise_web_search(query: str, **kwargs) -> dict:
    """
    Enterprise web search functionality.
    
    Args:
        query (str): Search query
        **kwargs: Additional search parameters
        
    Returns:
        dict: Enterprise search results
    """
    pass

def url_context(url: str, **kwargs) -> dict:
    """
    Extract context and content from a URL.
    
    Args:
        url (str): URL to extract context from
        **kwargs: Additional extraction parameters
        
    Returns:
        dict: URL content and metadata
    """
    pass

def exit_loop(**kwargs):
    """
    Exit loop functionality for LoopAgent.
    
    Args:
        **kwargs: Exit parameters
    """
    pass

def get_user_choice(choices: list, prompt: str = None, **kwargs):
    """
    Prompt user to make a choice from given options.
    
    Args:
        choices (list): List of available choices
        prompt (str, optional): Prompt message for the user
        **kwargs: Additional choice parameters
        
    Returns:
        Selected choice
    """
    pass

def load_artifacts(artifact_ids: list = None, **kwargs) -> dict:
    """
    Load artifacts from storage.
    
    Args:
        artifact_ids (list, optional): Specific artifact IDs to load
        **kwargs: Additional loading parameters
        
    Returns:
        dict: Loaded artifacts
    """
    pass

def load_memory(memory_keys: list = None, **kwargs) -> dict:
    """
    Load memory data.
    
    Args:
        memory_keys (list, optional): Specific memory keys to load
        **kwargs: Additional loading parameters
        
    Returns:
        dict: Loaded memory data
    """
    pass

def preload_memory(memory_data: dict, **kwargs):
    """
    Preload memory with data.
    
    Args:
        memory_data (dict): Memory data to preload
        **kwargs: Additional preloading parameters
    """
    pass

def transfer_to_agent(agent_name: str, message: str, **kwargs):
    """
    Transfer control to another agent.
    
    Args:
        agent_name (str): Name of the target agent
        message (str): Message to pass to the target agent
        **kwargs: Additional transfer parameters
    """
    pass
```

### Specialized Toolsets

Advanced toolsets for specific integrations and services.

```python { .api }
class APIHubToolset:
    """API Hub integration toolset."""
    
    def __init__(self, api_hub_config: dict, **kwargs):
        """
        Initialize API Hub toolset.
        
        Args:
            api_hub_config (dict): API Hub configuration
            **kwargs: Additional configuration parameters
        """
        pass

class VertexAiSearchTool(BaseTool):
    """Vertex AI search functionality."""
    
    def __init__(self, project_id: str, location: str, **kwargs):
        """
        Initialize Vertex AI search tool.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            **kwargs: Additional configuration parameters
        """
        pass

class MCPToolset:
    """Model Context Protocol toolset (Python 3.10+)."""
    
    def __init__(self, mcp_config: dict, **kwargs):
        """
        Initialize MCP toolset.
        
        Note: Requires Python 3.10 or higher.
        
        Args:
            mcp_config (dict): MCP configuration
            **kwargs: Additional configuration parameters
        """
        pass
```

### REST API Tools

Tools for working with REST APIs and OpenAPI specifications.

```python { .api }
class OpenAPIToolset:
    """OpenAPI specification-based toolset."""
    
    def __init__(self, openapi_spec: dict, base_url: str = None, **kwargs):
        """
        Initialize OpenAPI toolset.
        
        Args:
            openapi_spec (dict): OpenAPI specification
            base_url (str, optional): Base URL for API calls
            **kwargs: Additional configuration parameters
        """
        pass

class RestApiTool(BaseTool):
    """REST API tool for making HTTP requests."""
    
    def __init__(self, base_url: str, auth_config: dict = None, **kwargs):
        """
        Initialize REST API tool.
        
        Args:
            base_url (str): Base URL for the API
            auth_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass
```

## Usage Examples

### Creating Custom Function Tools

```python
from google.adk.tools import FunctionTool

def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width

# Wrap function as a tool
area_tool = FunctionTool(
    func=calculate_area,
    name="area_calculator",
    description="Calculate the area of a rectangle given length and width"
)

# Use with an agent
from google.adk.agents import Agent
agent = Agent(
    name="math_assistant",
    model="gemini-2.0-flash",
    tools=[area_tool]
)
```

### Using Built-in Tools

```python
from google.adk.tools import google_search, url_context
from google.adk.agents import Agent

# Create agent with built-in tools
agent = Agent(
    name="research_agent",
    model="gemini-2.0-flash",
    instruction="Help users research topics using web search and URL analysis.",
    tools=[google_search, url_context]
)
```

### Custom Tool Class

```python
from google.adk.tools import BaseTool, ToolContext

class WeatherTool(BaseTool):
    def __init__(self, api_key: str):
        super().__init__(
            name="weather_tool",
            description="Get current weather information for a location"
        )
        self.api_key = api_key
    
    def execute(self, context: ToolContext, location: str, **kwargs):
        # Implementation to fetch weather data
        return f"Weather in {location}: Sunny, 72°F"

# Use custom tool
weather_tool = WeatherTool(api_key="your-api-key")
agent = Agent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    tools=[weather_tool]
)
```

### Long-Running Tool

```python
from google.adk.tools import LongRunningFunctionTool
import time

def process_large_dataset(data_path: str) -> dict:
    """Process a large dataset - this might take a while."""
    time.sleep(10)  # Simulate long processing
    return {"status": "completed", "records_processed": 10000}

# Wrap as long-running tool with timeout
processing_tool = LongRunningFunctionTool(
    func=process_large_dataset,
    timeout=30,  # 30 second timeout
    name="dataset_processor"
)
```

### Agent as Tool

```python
from google.adk.tools import AgentTool
from google.adk.agents import Agent

# Create specialized agent
translator = Agent(
    name="translator",
    model="gemini-2.0-flash",
    instruction="Translate text between languages accurately."
)

# Wrap agent as a tool
translation_tool = AgentTool(agent=translator)

# Use in another agent
main_agent = Agent(
    name="multilingual_assistant",
    model="gemini-2.0-flash",
    tools=[translation_tool]
)
```

### OpenAPI Integration

```python
from google.adk.tools import OpenAPIToolset

# Load OpenAPI spec (could be from file or URL)
openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "My API", "version": "1.0.0"},
    "paths": { ... }  # API endpoints
}

# Create toolset from OpenAPI spec
api_toolset = OpenAPIToolset(
    openapi_spec=openapi_spec,
    base_url="https://api.example.com"
)

# Use with agent
agent = Agent(
    name="api_agent",
    model="gemini-2.0-flash",
    tools=api_toolset.get_tools()  # Get all tools from the toolset
)
```