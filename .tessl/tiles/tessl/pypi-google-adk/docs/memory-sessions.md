# Memory and Session Management

Infrastructure services for persistent memory, session state, and artifact storage with support for in-memory and cloud-based implementations.

## Capabilities

### Memory Services

Classes for managing persistent memory across agent interactions.

```python { .api }
class BaseMemoryService:
    """Base class for memory services."""
    
    def __init__(self, **kwargs):
        """
        Initialize base memory service.
        
        Args:
            **kwargs: Memory service configuration parameters
        """
        pass
    
    def store(self, key: str, value: any, **kwargs):
        """
        Store a value in memory.
        
        Args:
            key (str): Memory key
            value (any): Value to store
            **kwargs: Additional storage parameters
        """
        pass
    
    def retrieve(self, key: str, **kwargs) -> any:
        """
        Retrieve a value from memory.
        
        Args:
            key (str): Memory key
            **kwargs: Additional retrieval parameters
            
        Returns:
            any: Retrieved value or None if not found
        """
        pass
    
    def delete(self, key: str, **kwargs):
        """
        Delete a value from memory.
        
        Args:
            key (str): Memory key to delete
            **kwargs: Additional deletion parameters
        """
        pass
    
    def list_keys(self, prefix: str = None, **kwargs) -> list:
        """
        List memory keys.
        
        Args:
            prefix (str, optional): Key prefix filter
            **kwargs: Additional listing parameters
            
        Returns:
            list: List of memory keys
        """
        pass

class InMemoryMemoryService(BaseMemoryService):
    """In-memory memory implementation."""
    
    def __init__(self, **kwargs):
        """
        Initialize in-memory memory service.
        
        Args:
            **kwargs: Configuration parameters
        """
        pass

class VertexAiMemoryBankService(BaseMemoryService):
    """Vertex AI memory bank service."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        memory_bank_id: str = None,
        **kwargs
    ):
        """
        Initialize Vertex AI memory bank service.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            memory_bank_id (str, optional): Memory bank identifier
            **kwargs: Additional configuration parameters
        """
        pass

class VertexAiRagMemoryService(BaseMemoryService):
    """Vertex AI RAG memory service (optional dependency)."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        rag_corpus_id: str = None,
        **kwargs
    ):
        """
        Initialize Vertex AI RAG memory service.
        
        Note: Requires additional dependencies.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            rag_corpus_id (str, optional): RAG corpus identifier
            **kwargs: Additional configuration parameters
        """
        pass
```

### Session Services

Classes for managing session state and user interactions.

```python { .api }
class BaseSessionService:
    """Base class for session services."""
    
    def __init__(self, **kwargs):
        """
        Initialize base session service.
        
        Args:
            **kwargs: Session service configuration parameters
        """
        pass
    
    def create_session(self, session_id: str = None, **kwargs) -> 'Session':
        """
        Create a new session.
        
        Args:
            session_id (str, optional): Session identifier
            **kwargs: Additional session parameters
            
        Returns:
            Session: Created session object
        """
        pass
    
    def get_session(self, session_id: str, **kwargs) -> 'Session':
        """
        Retrieve an existing session.
        
        Args:
            session_id (str): Session identifier
            **kwargs: Additional retrieval parameters
            
        Returns:
            Session: Session object or None if not found
        """
        pass
    
    def update_session(self, session_id: str, state: 'State', **kwargs):
        """
        Update session state.
        
        Args:
            session_id (str): Session identifier
            state (State): New session state
            **kwargs: Additional update parameters
        """
        pass
    
    def delete_session(self, session_id: str, **kwargs):
        """
        Delete a session.
        
        Args:
            session_id (str): Session identifier
            **kwargs: Additional deletion parameters
        """
        pass

class InMemorySessionService(BaseSessionService):
    """In-memory session implementation."""
    
    def __init__(self, **kwargs):
        """
        Initialize in-memory session service.
        
        Args:
            **kwargs: Configuration parameters
        """
        pass

class VertexAiSessionService(BaseSessionService):
    """Vertex AI session service."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        **kwargs
    ):
        """
        Initialize Vertex AI session service.
        
        Args:
            project_id (str): Google Cloud project ID
            location (str): Vertex AI location
            **kwargs: Additional configuration parameters
        """
        pass

class DatabaseSessionService(BaseSessionService):
    """Database-backed session service (optional dependency)."""
    
    def __init__(
        self,
        connection_string: str,
        table_name: str = "sessions",
        **kwargs
    ):
        """
        Initialize database session service.
        
        Args:
            connection_string (str): Database connection string
            table_name (str): Session table name
            **kwargs: Additional configuration parameters
        """
        pass

class Session:
    """Session object for managing user interactions."""
    
    def __init__(
        self,
        session_id: str,
        state: 'State' = None,
        metadata: dict = None,
        **kwargs
    ):
        """
        Initialize session.
        
        Args:
            session_id (str): Session identifier
            state (State, optional): Session state
            metadata (dict, optional): Session metadata
            **kwargs: Additional session parameters
        """
        pass
    
    def get_state(self) -> 'State':
        """
        Get current session state.
        
        Returns:
            State: Current session state
        """
        pass
    
    def set_state(self, state: 'State'):
        """
        Set session state.
        
        Args:
            state (State): New session state
        """
        pass

class State:
    """Session state object."""
    
    def __init__(self, data: dict = None, **kwargs):
        """
        Initialize session state.
        
        Args:
            data (dict, optional): State data
            **kwargs: Additional state parameters
        """
        pass
    
    def get(self, key: str, default=None):
        """
        Get state value.
        
        Args:
            key (str): State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        pass
    
    def set(self, key: str, value: any):
        """
        Set state value.
        
        Args:
            key (str): State key
            value (any): Value to set
        """
        pass
    
    def to_dict(self) -> dict:
        """
        Convert state to dictionary.
        
        Returns:
            dict: State as dictionary
        """
        pass
```

### Artifact Services

Classes for managing artifacts and file storage.

```python { .api }
class BaseArtifactService:
    """Base class for artifact services."""
    
    def __init__(self, **kwargs):
        """
        Initialize base artifact service.
        
        Args:
            **kwargs: Artifact service configuration parameters
        """
        pass
    
    def store_artifact(
        self,
        artifact_id: str,
        data: bytes,
        content_type: str = None,
        **kwargs
    ):
        """
        Store an artifact.
        
        Args:
            artifact_id (str): Artifact identifier
            data (bytes): Artifact data
            content_type (str, optional): MIME content type
            **kwargs: Additional storage parameters
        """
        pass
    
    def retrieve_artifact(self, artifact_id: str, **kwargs) -> bytes:
        """
        Retrieve an artifact.
        
        Args:
            artifact_id (str): Artifact identifier
            **kwargs: Additional retrieval parameters
            
        Returns:
            bytes: Artifact data
        """
        pass
    
    def delete_artifact(self, artifact_id: str, **kwargs):
        """
        Delete an artifact.
        
        Args:
            artifact_id (str): Artifact identifier
            **kwargs: Additional deletion parameters
        """
        pass
    
    def list_artifacts(self, prefix: str = None, **kwargs) -> list:
        """
        List artifacts.
        
        Args:
            prefix (str, optional): Artifact ID prefix filter
            **kwargs: Additional listing parameters
            
        Returns:
            list: List of artifact IDs
        """
        pass

class InMemoryArtifactService(BaseArtifactService):
    """In-memory artifact service."""
    
    def __init__(self, **kwargs):
        """
        Initialize in-memory artifact service.
        
        Args:
            **kwargs: Configuration parameters
        """
        pass

class GcsArtifactService(BaseArtifactService):
    """Google Cloud Storage artifact service."""
    
    def __init__(
        self,
        bucket_name: str,
        project_id: str = None,
        credentials_path: str = None,
        **kwargs
    ):
        """
        Initialize GCS artifact service.
        
        Args:
            bucket_name (str): GCS bucket name
            project_id (str, optional): Google Cloud project ID
            credentials_path (str, optional): Path to service account credentials
            **kwargs: Additional configuration parameters
        """
        pass
```

## Usage Examples

### Basic Memory Usage

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.agents import Agent

# Create memory service
memory_service = InMemoryMemoryService()

# Store data
memory_service.store("user_preferences", {
    "language": "en",
    "theme": "dark",
    "notifications": True
})

# Configure agent with memory
agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    memory_service=memory_service
)

# Agent can now access stored memories
response = agent.run("What are my preferences?")
```

### Session Management

```python
from google.adk.sessions import InMemorySessionService, State
from google.adk.agents import Agent

# Create session service
session_service = InMemorySessionService()

# Create a new session
session = session_service.create_session("user-123")

# Set session state
state = State({
    "conversation_history": [],
    "current_task": "data_analysis",
    "user_context": {"role": "analyst"}
})
session.set_state(state)

# Use with agent
agent = Agent(
    name="session_agent",
    model="gemini-2.0-flash",
    session_service=session_service
)

# Agent maintains session context
response = agent.run("Continue with the analysis", session_id="user-123")
```

### Vertex AI Memory Integration

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.agents import Agent

# Configure Vertex AI memory
memory_service = VertexAiMemoryBankService(
    project_id="my-project",
    location="us-central1",
    memory_bank_id="my-memory-bank"
)

# Store long-term memories
memory_service.store("company_policies", {
    "vacation_policy": "...",
    "remote_work_policy": "...",
    "expense_policy": "..."
})

# Agent with persistent cloud memory
agent = Agent(
    name="hr_assistant",
    model="gemini-2.0-flash",
    memory_service=memory_service,
    instruction="Help employees with HR questions using company policies"
)
```

### Artifact Management

```python
from google.adk.artifacts import GcsArtifactService
from google.adk.agents import Agent

# Configure GCS artifact storage
artifact_service = GcsArtifactService(
    bucket_name="my-artifacts-bucket",
    project_id="my-project"
)

# Store document
with open("report.pdf", "rb") as f:
    artifact_service.store_artifact(
        "quarterly_report_q4",
        f.read(),
        content_type="application/pdf"
    )

# Agent with artifact access
agent = Agent(
    name="document_agent",
    model="gemini-2.0-flash",
    artifact_service=artifact_service
)

# Agent can access stored artifacts
response = agent.run("Summarize the Q4 quarterly report")
```

### Multi-Service Integration

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService
from google.adk.artifacts import GcsArtifactService
from google.adk.agents import Agent

# Configure all services
memory_service = VertexAiMemoryBankService(
    project_id="my-project",
    memory_bank_id="agent-memory"
)

session_service = VertexAiSessionService(
    project_id="my-project"
)

artifact_service = GcsArtifactService(
    bucket_name="agent-artifacts",
    project_id="my-project"
)

# Create comprehensive agent
enterprise_agent = Agent(
    name="enterprise_assistant",
    model="gemini-2.0-flash",
    memory_service=memory_service,
    session_service=session_service,
    artifact_service=artifact_service,
    instruction="Help with enterprise tasks using persistent memory and artifacts"
)
```

### Session State Management

```python
from google.adk.sessions import InMemorySessionService, Session, State

session_service = InMemorySessionService()

# Create session with initial state
initial_state = State({
    "workflow_step": 1,
    "collected_data": [],
    "pending_tasks": ["task1", "task2", "task3"]
})

session = session_service.create_session("workflow-session", state=initial_state)

# Update state as workflow progresses
current_state = session.get_state()
current_state.set("workflow_step", 2)
current_state.set("completed_task", "task1")

session.set_state(current_state)
session_service.update_session("workflow-session", current_state)
```

### Memory Search and Retrieval

```python
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()

# Store various memories
memory_service.store("meeting_notes_2024_01", "Team discussed Q1 goals...")
memory_service.store("meeting_notes_2024_02", "Reviewed project timeline...")
memory_service.store("user_profile", {"name": "John", "role": "Manager"})

# List and search memories
meeting_keys = memory_service.list_keys(prefix="meeting_notes")
print(f"Found {len(meeting_keys)} meeting notes")

# Retrieve specific memories
profile = memory_service.retrieve("user_profile")
print(f"User: {profile['name']}")
```