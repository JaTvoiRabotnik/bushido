# Advanced Features

Planning, evaluation, event system, and plugin framework for sophisticated agent behaviors and custom extensions.

## Capabilities

### Planning System

Classes for implementing planning and reasoning strategies in agents.

```python { .api }
class BasePlanner:
    """Base class for planners."""
    
    def __init__(self, **kwargs):
        """
        Initialize base planner.
        
        Args:
            **kwargs: Planner configuration parameters
        """
        pass
    
    def create_plan(
        self,
        goal: str,
        context: dict = None,
        constraints: list = None,
        **kwargs
    ) -> dict:
        """
        Create a plan to achieve the given goal.
        
        Args:
            goal (str): Goal to achieve
            context (dict, optional): Planning context
            constraints (list, optional): Planning constraints
            **kwargs: Additional planning parameters
            
        Returns:
            dict: Plan with steps and metadata
        """
        pass
    
    def execute_plan(self, plan: dict, **kwargs) -> dict:
        """
        Execute a generated plan.
        
        Args:
            plan (dict): Plan to execute
            **kwargs: Additional execution parameters
            
        Returns:
            dict: Execution results
        """
        pass
    
    def adapt_plan(self, plan: dict, feedback: dict, **kwargs) -> dict:
        """
        Adapt plan based on feedback.
        
        Args:
            plan (dict): Original plan
            feedback (dict): Execution feedback
            **kwargs: Additional adaptation parameters
            
        Returns:
            dict: Adapted plan
        """
        pass

class BuiltInPlanner(BasePlanner):
    """Built-in planner implementation."""
    
    def __init__(
        self,
        max_steps: int = 10,
        planning_model: str = None,
        **kwargs
    ):
        """
        Initialize built-in planner.
        
        Args:
            max_steps (int): Maximum planning steps
            planning_model (str, optional): Model for planning
            **kwargs: Additional configuration parameters
        """
        pass

class PlanReActPlanner(BasePlanner):
    """Plan-ReAct planner implementation."""
    
    def __init__(
        self,
        reasoning_model: str = None,
        action_model: str = None,
        **kwargs
    ):
        """
        Initialize Plan-ReAct planner.
        
        Args:
            reasoning_model (str, optional): Model for reasoning
            action_model (str, optional): Model for actions
            **kwargs: Additional configuration parameters
        """
        pass
```

### Evaluation Framework

Classes for evaluating agent performance and behavior.

```python { .api }
class AgentEvaluator:
    """Agent evaluation framework (optional dependency)."""
    
    def __init__(
        self,
        evaluation_metrics: list = None,
        benchmark_datasets: list = None,
        **kwargs
    ):
        """
        Initialize agent evaluator.
        
        Args:
            evaluation_metrics (list, optional): Metrics to evaluate
            benchmark_datasets (list, optional): Datasets for benchmarking
            **kwargs: Additional configuration parameters
        """
        pass
    
    def evaluate_agent(
        self,
        agent,
        test_cases: list,
        metrics: list = None,
        **kwargs
    ) -> dict:
        """
        Evaluate agent performance on test cases.
        
        Args:
            agent: Agent to evaluate
            test_cases (list): Test cases for evaluation
            metrics (list, optional): Specific metrics to compute
            **kwargs: Additional evaluation parameters
            
        Returns:
            dict: Evaluation results with scores and analysis
        """
        pass
    
    def compare_agents(
        self,
        agents: list,
        test_cases: list,
        **kwargs
    ) -> dict:
        """
        Compare multiple agents on same test cases.
        
        Args:
            agents (list): Agents to compare
            test_cases (list): Test cases for comparison
            **kwargs: Additional comparison parameters
            
        Returns:
            dict: Comparison results and rankings
        """
        pass
    
    def generate_report(self, evaluation_results: dict, **kwargs) -> str:
        """
        Generate evaluation report.
        
        Args:
            evaluation_results (dict): Results from evaluation
            **kwargs: Additional report parameters
            
        Returns:
            str: Formatted evaluation report
        """
        pass
```

### Event System

Classes for handling events and communication between agents.

```python { .api }
class Event:
    """Event object for agent communication."""
    
    def __init__(
        self,
        event_type: str,
        source: str,
        target: str = None,
        data: dict = None,
        timestamp: float = None,
        **kwargs
    ):
        """
        Initialize event.
        
        Args:
            event_type (str): Type of event
            source (str): Event source identifier
            target (str, optional): Event target identifier
            data (dict, optional): Event data payload
            timestamp (float, optional): Event timestamp
            **kwargs: Additional event parameters
        """
        pass
    
    def get_data(self) -> dict:
        """
        Get event data.
        
        Returns:
            dict: Event data payload
        """
        pass
    
    def set_data(self, data: dict):
        """
        Set event data.
        
        Args:
            data (dict): Event data to set
        """
        pass
    
    def to_dict(self) -> dict:
        """
        Convert event to dictionary.
        
        Returns:
            dict: Event as dictionary
        """
        pass

class EventActions:
    """Actions associated with events."""
    
    AGENT_START = "agent_start"
    AGENT_FINISH = "agent_finish"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    MESSAGE = "message"
    TRANSFER = "transfer"
    
    @classmethod
    def get_all_actions(cls) -> list:
        """
        Get all available event actions.
        
        Returns:
            list: List of event action types
        """
        pass
```

### Plugin System

Classes for creating and managing plugins to extend ADK functionality.

```python { .api }
class BasePlugin:
    """Base class for plugins."""
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = None,
        **kwargs
    ):
        """
        Initialize base plugin.
        
        Args:
            name (str): Plugin name
            version (str): Plugin version
            description (str, optional): Plugin description
            **kwargs: Additional plugin parameters
        """
        pass
    
    def initialize(self, context: dict = None):
        """
        Initialize the plugin.
        
        Args:
            context (dict, optional): Initialization context
        """
        pass
    
    def activate(self):
        """Activate the plugin."""
        pass
    
    def deactivate(self):
        """Deactivate the plugin."""
        pass
    
    def get_capabilities(self) -> list:
        """
        Get plugin capabilities.
        
        Returns:
            list: List of plugin capabilities
        """
        pass
    
    def handle_event(self, event: Event) -> dict:
        """
        Handle an event.
        
        Args:
            event (Event): Event to handle
            
        Returns:
            dict: Event handling result
        """
        pass
```

### Example Providers

Classes for managing examples and demonstrations for agents.

```python { .api }
class BaseExampleProvider:
    """Base class for example providers."""
    
    def __init__(self, **kwargs):
        """
        Initialize base example provider.
        
        Args:
            **kwargs: Provider configuration parameters
        """
        pass
    
    def get_examples(
        self,
        task_type: str = None,
        count: int = 5,
        **kwargs
    ) -> list:
        """
        Get examples for a task type.
        
        Args:
            task_type (str, optional): Type of task
            count (int): Number of examples to retrieve
            **kwargs: Additional retrieval parameters
            
        Returns:
            list: List of Example objects
        """
        pass
    
    def add_example(self, example: 'Example'):
        """
        Add an example to the provider.
        
        Args:
            example (Example): Example to add
        """
        pass

class Example:
    """Example object."""
    
    def __init__(
        self,
        input_text: str,
        output_text: str,
        task_type: str = None,
        metadata: dict = None,
        **kwargs
    ):
        """
        Initialize example.
        
        Args:
            input_text (str): Example input
            output_text (str): Example output
            task_type (str, optional): Type of task this example demonstrates
            metadata (dict, optional): Additional example metadata
            **kwargs: Additional example parameters
        """
        pass

class VertexAiExampleStore(BaseExampleProvider):
    """Vertex AI example store (optional dependency)."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        example_store_id: str = None,
        **kwargs
    ):
        """
        Initialize Vertex AI example store.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            example_store_id (str, optional): Example store identifier
            **kwargs: Additional configuration parameters
        """
        pass
```

## Usage Examples

### Planning with Agents

```python
from google.adk.planners import BuiltInPlanner
from google.adk.agents import Agent

# Create planner
planner = BuiltInPlanner(
    max_steps=8,
    planning_model="gemini-2.0-flash"
)

# Create planning agent
planning_agent = Agent(
    name="strategic_planner",
    model="gemini-2.0-flash",
    instruction="Create detailed plans to achieve complex goals",
    planner=planner
)

# Use agent with planning
response = planning_agent.run(
    "Create a plan to launch a new product in 6 months, "
    "including market research, development, and marketing phases"
)

# Get the generated plan
plan = planner.create_plan(
    goal="Launch new product in 6 months",
    context={"budget": 100000, "team_size": 5},
    constraints=["must complete market research first", "budget limit $100k"]
)

print(f"Plan steps: {len(plan['steps'])}")
for step in plan['steps']:
    print(f"- {step['description']} (Duration: {step['duration']})")
```

### Agent Evaluation

```python
from google.adk.evaluation import AgentEvaluator
from google.adk.agents import Agent

# Create test agents
agent_a = Agent(name="agent_a", model="gemini-2.0-flash")
agent_b = Agent(name="agent_b", model="gemini-2.0-flash", temperature=0.3)

# Create evaluator
evaluator = AgentEvaluator(
    evaluation_metrics=["accuracy", "relevance", "coherence"],
    benchmark_datasets=["qa_dataset", "reasoning_dataset"]
)

# Define test cases
test_cases = [
    {"input": "What is the capital of France?", "expected": "Paris"},
    {"input": "Explain photosynthesis", "expected": "Process where plants..."},
    {"input": "Solve: 2x + 5 = 15", "expected": "x = 5"}
]

# Evaluate single agent
results_a = evaluator.evaluate_agent(
    agent=agent_a,
    test_cases=test_cases,
    metrics=["accuracy", "relevance"]
)

# Compare multiple agents
comparison = evaluator.compare_agents(
    agents=[agent_a, agent_b],
    test_cases=test_cases
)

# Generate report
report = evaluator.generate_report(comparison)
print(report)
```

### Event System Usage

```python
from google.adk.events import Event, EventActions
from google.adk.agents import Agent

# Create event handler
def handle_tool_call(event: Event):
    print(f"Tool called: {event.get_data()['tool_name']}")
    print(f"Parameters: {event.get_data()['parameters']}")

def handle_agent_finish(event: Event):
    print(f"Agent finished: {event.source}")
    print(f"Result: {event.get_data()['result']}")

# Create events
tool_event = Event(
    event_type=EventActions.TOOL_CALL,
    source="research_agent",
    data={
        "tool_name": "google_search",
        "parameters": {"query": "AI advances 2024"}
    }
)

finish_event = Event(
    event_type=EventActions.AGENT_FINISH,
    source="research_agent",
    data={"result": "Research completed successfully"}
)

# Handle events
handle_tool_call(tool_event)
handle_agent_finish(finish_event)
```

### Custom Plugin Development

```python
from google.adk.plugins import BasePlugin
from google.adk.events import Event, EventActions

class LoggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="logging_plugin",
            version="1.0.0",
            description="Plugin for logging agent activities"
        )
        self.log_file = "agent_activities.log"
    
    def initialize(self, context=None):
        print(f"Initializing {self.name}")
        # Setup logging configuration
    
    def activate(self):
        print(f"Activating {self.name}")
    
    def handle_event(self, event: Event) -> dict:
        # Log different types of events
        if event.event_type == EventActions.TOOL_CALL:
            self._log_tool_call(event)
        elif event.event_type == EventActions.AGENT_FINISH:
            self._log_agent_finish(event)
        
        return {"status": "logged"}
    
    def _log_tool_call(self, event: Event):
        with open(self.log_file, "a") as f:
            f.write(f"TOOL_CALL: {event.source} -> {event.get_data()}\n")
    
    def _log_agent_finish(self, event: Event):
        with open(self.log_file, "a") as f:
            f.write(f"AGENT_FINISH: {event.source} completed\n")

# Use plugin
logging_plugin = LoggingPlugin()
logging_plugin.initialize()
logging_plugin.activate()

# Plugin handles events automatically when integrated with agents
```

### Example Management

```python
from google.adk.examples import BaseExampleProvider, Example

class CustomExampleProvider(BaseExampleProvider):
    def __init__(self):
        super().__init__()
        self.examples = []
    
    def add_example(self, example: Example):
        self.examples.append(example)
    
    def get_examples(self, task_type=None, count=5, **kwargs):
        if task_type:
            filtered = [e for e in self.examples if e.task_type == task_type]
            return filtered[:count]
        return self.examples[:count]

# Create example provider
provider = CustomExampleProvider()

# Add examples
provider.add_example(Example(
    input_text="What is machine learning?",
    output_text="Machine learning is a subset of AI that enables computers to learn...",
    task_type="explanation"
))

provider.add_example(Example(
    input_text="Calculate 15% of 200",
    output_text="15% of 200 is 30",
    task_type="calculation"
))

# Use with agent
from google.adk.agents import Agent

agent = Agent(
    name="learning_agent",
    model="gemini-2.0-flash",
    example_provider=provider
)

# Agent can use examples for few-shot learning
response = agent.run("What is deep learning?")  # Uses explanation examples
```

### ReAct Planning

```python
from google.adk.planners import PlanReActPlanner
from google.adk.agents import Agent
from google.adk.tools import google_search

# Create ReAct planner
react_planner = PlanReActPlanner(
    reasoning_model="gemini-2.0-flash",
    action_model="gemini-2.0-flash"
)

# Create agent with ReAct planning
react_agent = Agent(
    name="research_analyst",
    model="gemini-2.0-flash",
    instruction="Research topics systematically using reasoning and actions",
    tools=[google_search],
    planner=react_planner
)

# Agent uses Reason-Act-Observe cycles
response = react_agent.run(
    "Research the latest developments in quantum computing and "
    "analyze their potential impact on cybersecurity"
)
```

### Comprehensive Advanced Setup

```python
from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.adk.evaluation import AgentEvaluator
from google.adk.plugins import BasePlugin
from google.adk.examples import BaseExampleProvider
from google.adk.events import Event, EventActions

# Create advanced agent with all features
planner = BuiltInPlanner(max_steps=10)
evaluator = AgentEvaluator()
example_provider = CustomExampleProvider()

class AdvancedPlugin(BasePlugin):
    def handle_event(self, event):
        # Custom event handling logic
        return {"handled": True}

plugin = AdvancedPlugin()

# Advanced agent configuration
advanced_agent = Agent(
    name="advanced_assistant",
    model="gemini-2.0-flash",
    instruction="Advanced agent with planning, evaluation, and plugin support",
    planner=planner,
    example_provider=example_provider,
    plugins=[plugin]
)

# The agent now has access to all advanced features
response = advanced_agent.run("Solve a complex multi-step problem")
```