# Code Execution

Code execution framework supporting built-in, local, container-based, and Vertex AI code execution environments with safety controls.

## Capabilities

### Core Code Executor Classes

Base classes and implementations for executing code in various environments.

```python { .api }
class BaseCodeExecutor:
    """Base class for code executors."""
    
    def __init__(self, **kwargs):
        """
        Initialize base code executor.
        
        Args:
            **kwargs: Code executor configuration parameters
        """
        pass
    
    def execute(
        self,
        code: str,
        language: str,
        context: 'CodeExecutorContext' = None,
        **kwargs
    ) -> dict:
        """
        Execute code in the specified language.
        
        Args:
            code (str): Code to execute
            language (str): Programming language
            context (CodeExecutorContext, optional): Execution context
            **kwargs: Additional execution parameters
            
        Returns:
            dict: Execution result with output, errors, and metadata
        """
        pass
    
    def is_supported_language(self, language: str) -> bool:
        """
        Check if language is supported.
        
        Args:
            language (str): Programming language
            
        Returns:
            bool: True if language is supported
        """
        pass
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            list: List of supported programming languages
        """
        pass

class BuiltInCodeExecutor(BaseCodeExecutor):
    """Built-in code executor with safety controls."""
    
    def __init__(
        self,
        allowed_modules: list = None,
        timeout: float = 30,
        max_memory: int = 512,  # MB
        **kwargs
    ):
        """
        Initialize built-in code executor.
        
        Args:
            allowed_modules (list, optional): List of allowed Python modules
            timeout (float): Execution timeout in seconds
            max_memory (int): Maximum memory usage in MB
            **kwargs: Additional configuration parameters
        """
        pass

class UnsafeLocalCodeExecutor(BaseCodeExecutor):
    """Local code executor (unsafe - for development only)."""
    
    def __init__(
        self,
        working_directory: str = None,
        timeout: float = 60,
        **kwargs
    ):
        """
        Initialize unsafe local code executor.
        
        Warning: This executor runs code without sandboxing and should only
        be used in development environments.
        
        Args:
            working_directory (str, optional): Code execution directory
            timeout (float): Execution timeout in seconds
            **kwargs: Additional configuration parameters
        """
        pass

class VertexAiCodeExecutor(BaseCodeExecutor):
    """Vertex AI code executor (requires extensions)."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        **kwargs
    ):
        """
        Initialize Vertex AI code executor.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            **kwargs: Additional configuration parameters
        """
        pass

class ContainerCodeExecutor(BaseCodeExecutor):
    """Container-based code executor (requires extensions)."""
    
    def __init__(
        self,
        container_image: str,
        docker_config: dict = None,
        **kwargs
    ):
        """
        Initialize container code executor.
        
        Args:
            container_image (str): Docker container image
            docker_config (dict, optional): Docker configuration
            **kwargs: Additional configuration parameters
        """
        pass

class CodeExecutorContext:
    """Context for code execution."""
    
    def __init__(
        self,
        session_id: str = None,
        variables: dict = None,
        working_directory: str = None,
        **kwargs
    ):
        """
        Initialize code execution context.
        
        Args:
            session_id (str, optional): Session identifier
            variables (dict, optional): Pre-defined variables
            working_directory (str, optional): Working directory
            **kwargs: Additional context parameters
        """
        pass
    
    def set_variable(self, name: str, value: any):
        """
        Set context variable.
        
        Args:
            name (str): Variable name
            value (any): Variable value
        """
        pass
    
    def get_variable(self, name: str, default=None):
        """
        Get context variable.
        
        Args:
            name (str): Variable name
            default: Default value if not found
            
        Returns:
            Variable value or default
        """
        pass
```

## Usage Examples

### Basic Code Execution

```python
from google.adk.code_executors import BuiltInCodeExecutor

# Create safe code executor
executor = BuiltInCodeExecutor(
    allowed_modules=["math", "json", "datetime"],
    timeout=30,
    max_memory=256
)

# Execute Python code
result = executor.execute(
    code="""
import math
result = math.sqrt(16) + 5
print(f"Result: {result}")
""",
    language="python"
)

print(f"Output: {result['output']}")
print(f"Errors: {result['errors']}")
print(f"Exit Code: {result['exit_code']}")
```

### Code Execution with Context

```python
from google.adk.code_executors import BuiltInCodeExecutor, CodeExecutorContext

executor = BuiltInCodeExecutor()

# Create execution context with pre-defined variables
context = CodeExecutorContext(
    session_id="analysis-session",
    variables={
        "data": [1, 2, 3, 4, 5],
        "threshold": 3
    }
)

# Execute code with context
result = executor.execute(
    code="""
# Variables from context are available
filtered_data = [x for x in data if x > threshold]
print(f"Filtered data: {filtered_data}")
average = sum(filtered_data) / len(filtered_data)
print(f"Average: {average}")
""",
    language="python",
    context=context
)
```

### Agent with Code Execution

```python
from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import FunctionTool

# Create code executor
code_executor = BuiltInCodeExecutor(
    allowed_modules=["pandas", "numpy", "matplotlib"],
    timeout=60
)

# Create code execution tool
def execute_python_code(code: str) -> dict:
    """Execute Python code safely."""
    return code_executor.execute(code, "python")

code_tool = FunctionTool(
    func=execute_python_code,
    name="python_executor",
    description="Execute Python code for data analysis"
)

# Create agent with code execution capability
data_agent = Agent(
    name="data_scientist",
    model="gemini-2.0-flash",
    instruction="Help with data analysis using Python code execution",
    tools=[code_tool]
)

# Agent can now execute code
response = data_agent.run(
    "Analyze this dataset: [1, 5, 3, 8, 2, 9, 4]. "
    "Calculate mean, median, and standard deviation."
)
```

### Unsafe Local Execution (Development Only)

```python
from google.adk.code_executors import UnsafeLocalCodeExecutor

# Only use in development environments
executor = UnsafeLocalCodeExecutor(
    working_directory="/tmp/code_execution",
    timeout=30
)

# Can execute system commands and access filesystem
result = executor.execute(
    code="""
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# Write a file
with open("output.txt", "w") as f:
    f.write("Hello from code execution!")
""",
    language="python"
)

print(result['output'])
```

### Container-Based Execution

```python
from google.adk.code_executors import ContainerCodeExecutor

# Configure container executor
executor = ContainerCodeExecutor(
    container_image="python:3.9-slim",
    docker_config={
        "memory_limit": "512m",
        "cpu_limit": "1",
        "network_mode": "none"  # No network access
    }
)

# Execute code in container
result = executor.execute(
    code="""
import sys
print(f"Python version: {sys.version}")
print("Running in container!")

# Install and use a package
import subprocess
subprocess.run(["pip", "install", "requests"], check=True)

import requests
print("Requests library installed successfully")
""",
    language="python"
)
```

### Vertex AI Code Execution

```python
from google.adk.code_executors import VertexAiCodeExecutor

# Configure Vertex AI executor
executor = VertexAiCodeExecutor(
    project_id="my-project",
    location="us-central1"
)

# Execute code on Vertex AI
result = executor.execute(
    code="""
import pandas as pd
import numpy as np

# Create sample dataset
data = pd.DataFrame({
    'sales': np.random.randint(100, 1000, 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
})

# Analyze by region
analysis = data.groupby('region')['sales'].agg(['mean', 'median', 'std'])
print(analysis)
""",
    language="python"
)
```

### Multi-Language Support

```python
from google.adk.code_executors import BuiltInCodeExecutor

executor = BuiltInCodeExecutor()

# Check supported languages
languages = executor.get_supported_languages()
print(f"Supported languages: {languages}")

# Execute different languages
languages_to_test = ["python", "javascript", "sql"]

for lang in languages_to_test:
    if executor.is_supported_language(lang):
        print(f"Executing {lang}...")
        
        if lang == "python":
            code = "print('Hello from Python!')"
        elif lang == "javascript":
            code = "console.log('Hello from JavaScript!');"
        elif lang == "sql":
            code = "SELECT 'Hello from SQL!' as message;"
        
        result = executor.execute(code, lang)
        print(f"Output: {result['output']}")
```

### Error Handling and Debugging

```python
from google.adk.code_executors import BuiltInCodeExecutor

executor = BuiltInCodeExecutor()

# Execute code with potential errors
result = executor.execute(
    code="""
try:
    x = 10 / 0  # This will cause an error
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    x = 0

print(f"Final value: {x}")

# Also cause a syntax error
print("This line is fine")
invalid_syntax = 1 +  # This is invalid
""",
    language="python"
)

print(f"Exit code: {result['exit_code']}")
print(f"Output: {result['output']}")
print(f"Errors: {result['errors']}")
print(f"Execution time: {result.get('execution_time', 'N/A')}")
```

### Persistent Session Execution

```python
from google.adk.code_executors import BuiltInCodeExecutor, CodeExecutorContext

executor = BuiltInCodeExecutor()

# Create persistent context
context = CodeExecutorContext(session_id="data-analysis-session")

# Execute code in steps, maintaining state
step1_result = executor.execute(
    code="""
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print("DataFrame created")
print(df)
""",
    language="python",
    context=context
)

# Continue with same context - df is still available
step2_result = executor.execute(
    code="""
# df is still available from previous execution
df['C'] = df['A'] + df['B']
print("Added column C")
print(df)
total = df['C'].sum()
print(f"Total of column C: {total}")
""",
    language="python",
    context=context
)
```