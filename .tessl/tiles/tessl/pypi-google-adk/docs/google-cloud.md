# Google Cloud Integration

Specialized toolsets for Google Cloud services including BigQuery, Bigtable, Spanner, and Google APIs (Calendar, Gmail, Sheets, Docs, YouTube).

## Capabilities

### Database Toolsets

Toolsets for Google Cloud database services with authentication and query capabilities.

```python { .api }
class BigQueryToolset:
    """BigQuery database interaction toolset."""
    
    def __init__(
        self,
        project_id: str,
        credentials_config: 'BigQueryCredentialsConfig' = None,
        **kwargs
    ):
        """
        Initialize BigQuery toolset.
        
        Args:
            project_id (str): Google Cloud project ID
            credentials_config (BigQueryCredentialsConfig, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class BigQueryCredentialsConfig:
    """BigQuery credentials configuration."""
    
    def __init__(
        self,
        service_account_key: str = None,
        service_account_path: str = None,
        **kwargs
    ):
        """
        Initialize BigQuery credentials.
        
        Args:
            service_account_key (str, optional): Service account key JSON string
            service_account_path (str, optional): Path to service account key file
            **kwargs: Additional credential parameters
        """
        pass

class BigtableToolset:
    """Bigtable interaction toolset."""
    
    def __init__(
        self,
        project_id: str,
        instance_id: str,
        credentials_config: 'BigtableCredentialsConfig' = None,
        **kwargs
    ):
        """
        Initialize Bigtable toolset.
        
        Args:
            project_id (str): Google Cloud project ID
            instance_id (str): Bigtable instance ID
            credentials_config (BigtableCredentialsConfig, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class BigtableCredentialsConfig:
    """Bigtable credentials configuration."""
    
    def __init__(
        self,
        service_account_key: str = None,
        service_account_path: str = None,
        **kwargs
    ):
        """
        Initialize Bigtable credentials.
        
        Args:
            service_account_key (str, optional): Service account key JSON string
            service_account_path (str, optional): Path to service account key file
            **kwargs: Additional credential parameters
        """
        pass

class SpannerToolset:
    """Spanner database interaction toolset."""
    
    def __init__(
        self,
        project_id: str,
        instance_id: str,
        database_id: str,
        credentials_config: 'SpannerCredentialsConfig' = None,
        **kwargs
    ):
        """
        Initialize Spanner toolset.
        
        Args:
            project_id (str): Google Cloud project ID
            instance_id (str): Spanner instance ID
            database_id (str): Spanner database ID
            credentials_config (SpannerCredentialsConfig, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class SpannerCredentialsConfig:
    """Spanner credentials configuration."""
    
    def __init__(
        self,
        service_account_key: str = None,
        service_account_path: str = None,
        **kwargs
    ):
        """
        Initialize Spanner credentials.
        
        Args:
            service_account_key (str, optional): Service account key JSON string
            service_account_path (str, optional): Path to service account key file
            **kwargs: Additional credential parameters
        """
        pass
```

### Google API Integration

Toolsets for Google APIs including Workspace applications and YouTube.

```python { .api }
class GoogleApiToolset:
    """Generic Google API toolset."""
    
    def __init__(
        self,
        service_name: str,
        version: str,
        credentials_config: dict = None,
        **kwargs
    ):
        """
        Initialize Google API toolset.
        
        Args:
            service_name (str): Google API service name
            version (str): API version
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class GoogleApiTool:
    """Individual Google API tool."""
    
    def __init__(
        self,
        api_method: str,
        service_name: str,
        version: str,
        **kwargs
    ):
        """
        Initialize Google API tool.
        
        Args:
            api_method (str): Specific API method to call
            service_name (str): Google API service name
            version (str): API version
            **kwargs: Additional configuration parameters
        """
        pass

class CalendarToolset:
    """Google Calendar integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize Calendar toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class GmailToolset:
    """Gmail integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize Gmail toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class SheetsToolset:
    """Google Sheets integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize Sheets toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class SlidesToolset:
    """Google Slides integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize Slides toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class DocsToolset:
    """Google Docs integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize Docs toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass

class YoutubeToolset:
    """YouTube API integration toolset."""
    
    def __init__(self, credentials_config: dict = None, **kwargs):
        """
        Initialize YouTube toolset.
        
        Args:
            credentials_config (dict, optional): Authentication configuration
            **kwargs: Additional configuration parameters
        """
        pass
```

## Usage Examples

### BigQuery Integration

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.agents import Agent

# Configure BigQuery credentials
credentials = BigQueryCredentialsConfig(
    service_account_path="/path/to/service-account.json"
)

# Create BigQuery toolset
bq_toolset = BigQueryToolset(
    project_id="my-project",
    credentials_config=credentials
)

# Use with agent
agent = Agent(
    name="data_analyst",
    model="gemini-2.0-flash",
    instruction="Help analyze data using BigQuery",
    tools=bq_toolset.get_tools()
)

# Example query through agent
response = agent.run("Query the sales table to find top 10 products by revenue")
```

### Gmail Integration

```python
from google.adk.tools.google_api_tool import GmailToolset
from google.adk.agents import Agent

# Configure Gmail toolset
gmail_toolset = GmailToolset(
    credentials_config={
        "type": "oauth2",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "refresh_token": "your-refresh-token"
    }
)

# Create email assistant
email_agent = Agent(
    name="email_assistant",
    model="gemini-2.0-flash",
    instruction="Help manage emails efficiently",
    tools=gmail_toolset.get_tools()
)

# Use agent to manage emails
response = email_agent.run("Send an email to john@example.com about the meeting tomorrow")
```

### Google Sheets Integration

```python
from google.adk.tools.google_api_tool import SheetsToolset
from google.adk.agents import Agent

# Configure Sheets toolset
sheets_toolset = SheetsToolset(
    credentials_config={
        "service_account_path": "/path/to/credentials.json"
    }
)

# Create spreadsheet assistant
sheets_agent = Agent(
    name="sheets_assistant",
    model="gemini-2.0-flash",
    instruction="Help manage and analyze Google Sheets data",
    tools=sheets_toolset.get_tools()
)

# Use agent to work with sheets
response = sheets_agent.run(
    "Update the budget spreadsheet with Q4 projections: "
    "https://docs.google.com/spreadsheets/d/spreadsheet-id"
)
```

### Calendar Integration

```python
from google.adk.tools.google_api_tool import CalendarToolset
from google.adk.agents import Agent

# Configure Calendar toolset
calendar_toolset = CalendarToolset(
    credentials_config={
        "oauth2_credentials": "path/to/oauth2.json"
    }
)

# Create calendar assistant
calendar_agent = Agent(
    name="calendar_assistant",
    model="gemini-2.0-flash",
    instruction="Help manage calendar events and scheduling",
    tools=calendar_toolset.get_tools()
)

# Schedule meetings
response = calendar_agent.run(
    "Schedule a team meeting for next Tuesday at 2 PM, "
    "invite team@company.com, and set up a video call"
)
```

### Multi-Service Integration

```python
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.google_api_tool import SheetsToolset, GmailToolset
from google.adk.agents import Agent

# Configure multiple Google services
bq_toolset = BigQueryToolset(project_id="my-project")
sheets_toolset = SheetsToolset()
gmail_toolset = GmailToolset()

# Create comprehensive business assistant
business_agent = Agent(
    name="business_assistant",
    model="gemini-2.0-flash",
    instruction="Help with business operations using Google services",
    tools=[
        *bq_toolset.get_tools(),
        *sheets_toolset.get_tools(),
        *gmail_toolset.get_tools()
    ]
)

# Complex business workflow
response = business_agent.run(
    "Generate a sales report from BigQuery data, "
    "create a summary in Google Sheets, "
    "and email it to the sales team"
)
```

### Bigtable Usage

```python
from google.adk.tools.bigtable import BigtableToolset, BigtableCredentialsConfig
from google.adk.agents import Agent

# Configure Bigtable
credentials = BigtableCredentialsConfig(
    service_account_path="/path/to/service-account.json"
)

bigtable_toolset = BigtableToolset(
    project_id="my-project",
    instance_id="my-instance",
    credentials_config=credentials
)

# Create NoSQL data agent
nosql_agent = Agent(
    name="nosql_assistant",
    model="gemini-2.0-flash",
    instruction="Help manage Bigtable data operations",
    tools=bigtable_toolset.get_tools()
)

# Query Bigtable
response = nosql_agent.run(
    "Retrieve user activity data for user ID 12345 from the last 30 days"
)
```

### YouTube API Integration

```python
from google.adk.tools.google_api_tool import YoutubeToolset
from google.adk.agents import Agent

# Configure YouTube toolset
youtube_toolset = YoutubeToolset(
    credentials_config={
        "api_key": "your-youtube-api-key"
    }
)

# Create content manager agent
content_agent = Agent(
    name="content_manager",
    model="gemini-2.0-flash",
    instruction="Help manage YouTube content and analytics",
    tools=youtube_toolset.get_tools()
)

# Analyze channel performance
response = content_agent.run(
    "Analyze the performance of my latest videos and suggest improvements"
)
```

### Custom Google API Integration

```python
from google.adk.tools.google_api_tool import GoogleApiToolset
from google.adk.agents import Agent

# Create custom Google API toolset
custom_api_toolset = GoogleApiToolset(
    service_name="customsearch",
    version="v1",
    credentials_config={
        "api_key": "your-api-key"
    }
)

# Use with agent
search_agent = Agent(
    name="custom_search_agent",
    model="gemini-2.0-flash",
    tools=custom_api_toolset.get_tools()
)
```