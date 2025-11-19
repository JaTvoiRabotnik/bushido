from abc import ABC, abstractmethod
from typing import Any, List, Dict
from google.adk.tools import FunctionTool

class GameAgentAdapter(ABC):
    """
    Translates game state into agent-friendly context.
    Decouples the game logic from how the agent interacts with it.
    """
    
    @abstractmethod
    def get_system_instruction(self, player_state: Any) -> str:
        """Get the system instruction for the agent based on player state"""
        pass
    
    @abstractmethod
    def get_tools(self, player_state: Any, game_state: Any) -> List[FunctionTool]:
        """Get the tools available to the agent"""
        pass
    
    @abstractmethod
    def parse_response(self, response: str, player_state: Any, game_state: Any) -> Dict[str, Any]:
        """Parse the agent's response into a game decision"""
        pass
