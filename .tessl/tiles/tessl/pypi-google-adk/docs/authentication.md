# Authentication

Authentication framework supporting OAuth2, OpenID Connect, and Google Cloud authentication with configurable schemes and credential management.

## Capabilities

### Authentication Core Classes

Base classes for authentication credentials and configuration.

```python { .api }
class AuthCredential:
    """Authentication credential object."""
    
    def __init__(
        self,
        credential_type: 'AuthCredentialTypes',
        credential_data: dict,
        **kwargs
    ):
        """
        Initialize authentication credential.
        
        Args:
            credential_type (AuthCredentialTypes): Type of credential
            credential_data (dict): Credential data
            **kwargs: Additional credential parameters
        """
        pass
    
    def get_credential_data(self) -> dict:
        """
        Get credential data.
        
        Returns:
            dict: Credential data
        """
        pass
    
    def is_valid(self) -> bool:
        """
        Check if credential is valid.
        
        Returns:
            bool: True if credential is valid
        """
        pass

class AuthCredentialTypes:
    """Types of authentication credentials."""
    
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"
    OPENID_CONNECT = "openid_connect"
    BASIC_AUTH = "basic_auth"

class AuthConfig:
    """Authentication configuration."""
    
    def __init__(
        self,
        auth_schemes: list = None,
        default_scheme: str = None,
        **kwargs
    ):
        """
        Initialize authentication configuration.
        
        Args:
            auth_schemes (list, optional): List of authentication schemes
            default_scheme (str, optional): Default authentication scheme
            **kwargs: Additional configuration parameters
        """
        pass
    
    def add_scheme(self, scheme: 'AuthScheme'):
        """
        Add authentication scheme.
        
        Args:
            scheme (AuthScheme): Authentication scheme to add
        """
        pass
    
    def get_scheme(self, scheme_name: str) -> 'AuthScheme':
        """
        Get authentication scheme by name.
        
        Args:
            scheme_name (str): Scheme name
            
        Returns:
            AuthScheme: Authentication scheme
        """
        pass
```

### Authentication Handlers

Classes for handling different authentication methods.

```python { .api }
class AuthHandler:
    """Authentication handler."""
    
    def __init__(self, auth_config: AuthConfig, **kwargs):
        """
        Initialize authentication handler.
        
        Args:
            auth_config (AuthConfig): Authentication configuration
            **kwargs: Additional handler parameters
        """
        pass
    
    def authenticate(self, credential: AuthCredential) -> dict:
        """
        Authenticate using provided credential.
        
        Args:
            credential (AuthCredential): Authentication credential
            
        Returns:
            dict: Authentication result with tokens/headers
        """
        pass
    
    def refresh_token(self, credential: AuthCredential) -> AuthCredential:
        """
        Refresh authentication token.
        
        Args:
            credential (AuthCredential): Credential with refresh token
            
        Returns:
            AuthCredential: Updated credential with new token
        """
        pass
    
    def validate_credential(self, credential: AuthCredential) -> bool:
        """
        Validate authentication credential.
        
        Args:
            credential (AuthCredential): Credential to validate
            
        Returns:
            bool: True if credential is valid
        """
        pass

class OAuth2Auth(AuthHandler):
    """OAuth2 authentication."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        scopes: list = None,
        **kwargs
    ):
        """
        Initialize OAuth2 authentication.
        
        Args:
            client_id (str): OAuth2 client ID
            client_secret (str): OAuth2 client secret
            auth_url (str): Authorization URL
            token_url (str): Token URL
            scopes (list, optional): OAuth2 scopes
            **kwargs: Additional OAuth2 parameters
        """
        pass
    
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Get OAuth2 authorization URL.
        
        Args:
            redirect_uri (str): Redirect URI after authorization
            state (str, optional): State parameter for security
            
        Returns:
            str: Authorization URL
        """
        pass
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> AuthCredential:
        """
        Exchange authorization code for access token.
        
        Args:
            code (str): Authorization code
            redirect_uri (str): Redirect URI used in authorization
            
        Returns:
            AuthCredential: Credential with access token
        """
        pass

class OpenIdConnectWithConfig:
    """OpenID Connect authentication."""
    
    def __init__(
        self,
        issuer_url: str,
        client_id: str,
        client_secret: str = None,
        **kwargs
    ):
        """
        Initialize OpenID Connect authentication.
        
        Args:
            issuer_url (str): OIDC issuer URL
            client_id (str): OIDC client ID
            client_secret (str, optional): OIDC client secret
            **kwargs: Additional OIDC parameters
        """
        pass
    
    def get_user_info(self, access_token: str) -> dict:
        """
        Get user information from OIDC provider.
        
        Args:
            access_token (str): Access token
            
        Returns:
            dict: User information
        """
        pass
    
    def validate_id_token(self, id_token: str) -> dict:
        """
        Validate and decode ID token.
        
        Args:
            id_token (str): ID token to validate
            
        Returns:
            dict: Decoded token claims
        """
        pass
```

### Authentication Schemes

Classes for defining authentication schemes and types.

```python { .api }
class AuthScheme:
    """Authentication scheme definition."""
    
    def __init__(
        self,
        name: str,
        scheme_type: 'AuthSchemeType',
        config: dict,
        **kwargs
    ):
        """
        Initialize authentication scheme.
        
        Args:
            name (str): Scheme name
            scheme_type (AuthSchemeType): Type of authentication scheme
            config (dict): Scheme configuration
            **kwargs: Additional scheme parameters
        """
        pass
    
    def get_config(self) -> dict:
        """
        Get scheme configuration.
        
        Returns:
            dict: Scheme configuration
        """
        pass
    
    def create_credential(self, credential_data: dict) -> AuthCredential:
        """
        Create credential for this scheme.
        
        Args:
            credential_data (dict): Credential data
            
        Returns:
            AuthCredential: Created credential
        """
        pass

class AuthSchemeType:
    """Types of authentication schemes."""
    
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "openid_connect"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
```

## Usage Examples

### OAuth2 Authentication

```python
from google.adk.auth import OAuth2Auth, AuthCredential, AuthCredentialTypes

# Configure OAuth2
oauth2_auth = OAuth2Auth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    auth_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"]
)

# Get authorization URL
auth_url = oauth2_auth.get_authorization_url(
    redirect_uri="http://localhost:8080/callback",
    state="random-state-string"
)
print(f"Visit: {auth_url}")

# After user authorization, exchange code for token
credential = oauth2_auth.exchange_code_for_token(
    code="authorization-code-from-callback",
    redirect_uri="http://localhost:8080/callback"
)

# Use credential with agents
from google.adk.agents import Agent
agent = Agent(
    name="gmail_agent",
    model="gemini-2.0-flash",
    auth_credential=credential
)
```

### Service Account Authentication

```python
from google.adk.auth import AuthCredential, AuthCredentialTypes

# Load service account credentials
with open("service-account.json", "r") as f:
    service_account_data = json.load(f)

# Create service account credential
credential = AuthCredential(
    credential_type=AuthCredentialTypes.SERVICE_ACCOUNT,
    credential_data=service_account_data
)

# Use with Google Cloud services
from google.adk.tools.bigquery import BigQueryToolset
bq_toolset = BigQueryToolset(
    project_id="my-project",
    auth_credential=credential
)
```

### API Key Authentication

```python
from google.adk.auth import AuthCredential, AuthCredentialTypes

# Create API key credential
api_key_credential = AuthCredential(
    credential_type=AuthCredentialTypes.API_KEY,
    credential_data={
        "api_key": "your-api-key",
        "header_name": "X-API-Key"  # or "Authorization"
    }
)

# Use with tools that require API keys
from google.adk.tools import RestApiTool
api_tool = RestApiTool(
    base_url="https://api.example.com",
    auth_credential=api_key_credential
)
```

### OpenID Connect Authentication

```python
from google.adk.auth import OpenIdConnectWithConfig, AuthCredential

# Configure OIDC
oidc_auth = OpenIdConnectWithConfig(
    issuer_url="https://accounts.google.com",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Validate ID token
user_info = oidc_auth.validate_id_token("jwt-id-token")
print(f"User: {user_info['email']}")

# Get additional user info
user_profile = oidc_auth.get_user_info("access-token")
```

### Authentication Configuration

```python
from google.adk.auth import AuthConfig, AuthScheme, AuthSchemeType

# Create authentication schemes
oauth2_scheme = AuthScheme(
    name="google_oauth2",
    scheme_type=AuthSchemeType.OAUTH2,
    config={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "auth_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token"
    }
)

api_key_scheme = AuthScheme(
    name="api_key_auth",
    scheme_type=AuthSchemeType.API_KEY,
    config={
        "header_name": "X-API-Key"
    }
)

# Configure authentication
auth_config = AuthConfig(
    auth_schemes=[oauth2_scheme, api_key_scheme],
    default_scheme="google_oauth2"
)

# Use with authentication handler
from google.adk.auth import AuthHandler
auth_handler = AuthHandler(auth_config)
```

### Multi-Service Authentication

```python
from google.adk.auth import AuthConfig, OAuth2Auth, AuthCredential
from google.adk.agents import Agent

# Configure different auth methods for different services
google_oauth = OAuth2Auth(
    client_id="google-client-id",
    client_secret="google-client-secret",
    auth_url="https://accounts.google.com/o/oauth2/auth",
    token_url="https://oauth2.googleapis.com/token"
)

# Create credentials for different services
gmail_credential = google_oauth.exchange_code_for_token("gmail-auth-code", "redirect-uri")
sheets_credential = google_oauth.exchange_code_for_token("sheets-auth-code", "redirect-uri")

# Create agent with multiple credentials
multi_service_agent = Agent(
    name="office_assistant",
    model="gemini-2.0-flash",
    auth_credentials={
        "gmail": gmail_credential,
        "sheets": sheets_credential
    }
)
```

### Token Refresh

```python
from google.adk.auth import OAuth2Auth, AuthHandler

oauth2_auth = OAuth2Auth(
    client_id="client-id",
    client_secret="client-secret",
    auth_url="auth-url",
    token_url="token-url"
)

auth_handler = AuthHandler(auth_config)

# Check if token needs refresh
if not auth_handler.validate_credential(existing_credential):
    # Refresh the token
    refreshed_credential = auth_handler.refresh_token(existing_credential)
    
    # Update agent with new credential
    agent.update_auth_credential(refreshed_credential)
```

### Custom Authentication Scheme

```python
from google.adk.auth import AuthScheme, AuthSchemeType, AuthCredential

# Define custom authentication scheme
custom_scheme = AuthScheme(
    name="custom_auth",
    scheme_type=AuthSchemeType.BEARER_TOKEN,
    config={
        "token_endpoint": "https://auth.example.com/token",
        "username_field": "username",
        "password_field": "password"
    }
)

# Create credential for custom scheme
custom_credential = custom_scheme.create_credential({
    "username": "user@example.com",
    "password": "secure-password"
})

# Use with tools
from google.adk.tools import RestApiTool
custom_api_tool = RestApiTool(
    base_url="https://api.example.com",
    auth_credential=custom_credential
)
```