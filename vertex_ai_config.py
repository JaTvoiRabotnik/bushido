"""
Vertex AI Deployment Configuration for Bushido Testing Agent

This configuration ensures secure deployment without storing secrets in files.
All sensitive information should be passed through environment variables or
Vertex AI's secret manager.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class DeploymentConfig:
    """
    Configuration for Vertex AI deployment
    Pattern: Separation of Concerns (book page 281)
    """
    
    # Google Cloud Configuration (from environment)
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Model Configuration
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7  # For human-like variation
    max_tokens: int = 2048
    
    # Simulation Configuration
    max_parallel_games: int = 5  # Resource-aware optimization
    max_turns_per_game: int = 10  # Safety limit
    default_simulation_count: int = 10
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_structured_logging: bool = True
    log_to_cloud: bool = os.getenv("ENABLE_CLOUD_LOGGING", "true").lower() == "true"
    
    # Storage Configuration (using GCS for results)
    results_bucket: str = os.getenv("RESULTS_BUCKET", "")
    results_prefix: str = "bushido-simulations/"
    
    # Agent Configuration
    enable_reasoning_traces: bool = True
    enable_emotion_tracking: bool = True
    enable_strategy_memory: bool = True
    
    # Performance Configuration
    request_timeout: int = 300  # 5 minutes for complex games
    batch_size: int = 5  # Number of games to run in parallel
    
    @classmethod
    def from_env(cls) -> "DeploymentConfig":
        """Load configuration from environment variables"""
        return cls()
    
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set")
        
        return True
    
    def to_vertex_ai_config(self) -> dict:
        """Convert to Vertex AI configuration format"""
        return {
            "project": self.project_id,
            "location": self.location,
            "staging_bucket": f"gs://{self.results_bucket}/staging" if self.results_bucket else None,
            "experiment": "bushido-game-testing",
            "experiment_description": "Automated playtesting with human-like agents",
            "experiment_run": f"run-{os.getenv('RUN_ID', 'default')}",
            "enable_web_access": False,  # Agents don't need web access
            "network": os.getenv("VPC_NETWORK", ""),  # Optional VPC for security
            "service_account": os.getenv("SERVICE_ACCOUNT", ""),  # Optional custom SA
            "encryption_spec_key_name": os.getenv("CMEK_KEY", ""),  # Optional CMEK
        }

# ==================== VERTEX AI JOB DEFINITION ====================

VERTEX_AI_JOB_SPEC = {
    "display_name": "bushido-game-testing",
    "python_package_spec": {
        "executor_image_uri": "gcr.io/cloud-aiplatform/training/pytorch-gpu.1-13:latest",
        "package_uris": ["gs://{bucket}/packages/bushido_agent.tar.gz"],
        "python_module": "bushido_test_agent",
        "args": [
            "--num_simulations", "{num_simulations}",
            "--output_path", "gs://{bucket}/{prefix}",
            "--enable_evaluation", "true"
        ],
    },
    "replica_count": 1,
    "machine_spec": {
        "machine_type": "n1-standard-4",  # Reasonable for our workload
        "accelerator_type": "",  # No GPU needed for LLM API calls
        "accelerator_count": 0,
    },
    "scheduling": {
        "timeout": "3600s",  # 1 hour maximum
        "restart_job_on_worker_restart": False,
    },
    "labels": {
        "application": "bushido-testing",
        "framework": "google-adk",
        "type": "simulation"
    }
}

# ==================== SECRET MANAGEMENT ====================

def get_api_key() -> str:
    """
    Retrieve API key from environment or Secret Manager
    Never store keys in code or configuration files!
    """
    
    # First try environment variable
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key:
        return api_key
    
    # Try Google Secret Manager (recommended for production)
    try:
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        secret_name = "google-ai-api-key"
        
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")
        
        return api_key
    except Exception as e:
        print(f"Warning: Could not retrieve API key from Secret Manager: {e}")
        print("Please set GOOGLE_AI_API_KEY environment variable")
        return ""

# ==================== INITIALIZATION SCRIPT ====================

def initialize_vertex_ai():
    """Initialize Vertex AI with proper configuration"""
    
    import vertexai
    from google.oauth2 import service_account
    
    config = DeploymentConfig.from_env()
    config.validate()
    
    # Initialize with service account if provided
    credentials = None
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )
    
    vertexai.init(
        project=config.project_id,
        location=config.location,
        credentials=credentials,
        experiment=config.to_vertex_ai_config().get("experiment"),
        experiment_description=config.to_vertex_ai_config().get("experiment_description"),
    )
    
    return config

# ==================== DEPLOYMENT HELPER ====================

def deploy_to_vertex_ai():
    """
    Deploy the agent system to Vertex AI
    This should be run from a deployment script
    """
    
    from google.cloud import aiplatform
    
    config = DeploymentConfig.from_env()
    config.validate()
    
    aiplatform.init(
        project=config.project_id,
        location=config.location,
        staging_bucket=f"gs://{config.results_bucket}/staging"
    )
    
    # Create custom job
    job = aiplatform.CustomJob(
        display_name="bushido-game-testing",
        worker_pool_specs=[VERTEX_AI_JOB_SPEC],
        labels={
            "application": "bushido",
            "type": "testing-agent"
        }
    )
    
    # Run the job
    job.run(
        service_account=os.getenv("SERVICE_ACCOUNT"),
        network=os.getenv("VPC_NETWORK"),
        sync=False,  # Run asynchronously
        create_request_timeout=600,
    )
    
    print(f"Job deployed: {job.resource_name}")
    print(f"Monitor at: {job.dashboard_uri}")
    
    return job

if __name__ == "__main__":
    # Example: Validate configuration
    config = DeploymentConfig.from_env()
    
    print("Deployment Configuration:")
    print(f"  Project: {config.project_id or 'NOT SET'}")
    print(f"  Location: {config.location}")
    print(f"  Model: {config.model_name}")
    print(f"  Results Bucket: {config.results_bucket or 'NOT SET'}")
    
    if config.project_id:
        print("\nConfiguration is valid for deployment")
    else:
        print("\nConfiguration is incomplete - set required environment variables")
