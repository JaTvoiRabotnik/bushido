from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for agents"""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 1024
    
    # Simulation settings
    max_turns: int = 10
    honor_restriction_turn: int = 3
    
    # Vertex AI settings
    project_id: str = ""
    location: str = "us-central1"

# Global configuration instance
settings = AgentConfig()
