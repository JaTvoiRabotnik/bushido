"""
Abstract Game Interface for Playtesting Framework
Defines the contract that all game implementations must follow
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from google.adk.tools import FunctionTool


class GameInterface(ABC):
    """
    Abstract interface that all games must implement
    This allows the playtesting framework to work with any game
    """

    @abstractmethod
    def get_game_name(self) -> str:
        """Return the name of the game"""
        pass

    @abstractmethod
    def get_game_description(self) -> str:
        """Return a description of the game for display purposes"""
        pass

    @abstractmethod
    def create_player_tools(self, player_state: Any, game_state: Any) -> List[FunctionTool]:
        """
        Create game-specific tools for the AI agent

        Args:
            player_state: The state of the current player
            game_state: The overall game state

        Returns:
            List of FunctionTool objects the agent can use to query game state
        """
        pass

    @abstractmethod
    def get_agent_instruction(self, player_state: Any) -> str:
        """
        Get the main instruction prompt for the AI agent

        Args:
            player_state: The state of the player this agent controls

        Returns:
            Instruction string for the agent
        """
        pass

    @abstractmethod
    def get_persona_instructions(self, personality: Any) -> str:
        """
        Get personality-specific playing instructions

        Args:
            personality: The personality trait/type

        Returns:
            Personality-specific instructions
        """
        pass

    @abstractmethod
    def parse_decision(self, response: str, player_state: Any, game_state: Any) -> Dict[str, Any]:
        """
        Parse the AI agent's response into a game decision

        Args:
            response: The full text response from the AI
            player_state: The state of the player making the decision
            game_state: The overall game state

        Returns:
            Dictionary containing parsed decision with metrics
        """
        pass

    @abstractmethod
    def initialize_players(self, personas: Tuple[Any, Any], game_id: str) -> Tuple[Any, Any]:
        """
        Initialize player states for a new game

        Args:
            personas: Tuple of (persona1, persona2)
            game_id: Unique identifier for this game

        Returns:
            Tuple of (player1_state, player2_state)
        """
        pass

    @abstractmethod
    def initialize_game_state(self, game_id: str, player1: Any, player2: Any) -> Any:
        """
        Initialize the game state

        Args:
            game_id: Unique identifier for this game
            player1: First player state
            player2: Second player state

        Returns:
            Initialized game state object
        """
        pass

    @abstractmethod
    def resolve_turn(
        self,
        game_state: Any,
        player1_decision: Dict[str, Any],
        player2_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve a turn given both players' decisions

        Args:
            game_state: Current game state
            player1_decision: First player's decision
            player2_decision: Second player's decision

        Returns:
            Dictionary containing turn results
        """
        pass

    @abstractmethod
    def update_game_state(self, game_state: Any, turn_result: Dict[str, Any]) -> None:
        """
        Update the game state after turn resolution

        Args:
            game_state: Current game state (modified in place)
            turn_result: Results from resolve_turn
        """
        pass

    @abstractmethod
    def check_victory(self, game_state: Any) -> Any:
        """
        Check if the game has ended and who won

        Args:
            game_state: Current game state

        Returns:
            Winner identifier (or None if game continues)
        """
        pass

    @abstractmethod
    def get_game_summary(self, game_state: Any, winner: Any) -> Dict[str, Any]:
        """
        Generate a summary of the completed game

        Args:
            game_state: Final game state
            winner: Winner identifier from check_victory

        Returns:
            Dictionary containing game summary data
        """
        pass

    @abstractmethod
    def generate_persona_pairs(self, count: int) -> List[Tuple[Any, Any]]:
        """
        Generate diverse persona pairs for testing

        Args:
            count: Number of persona pairs to generate

        Returns:
            List of (persona1, persona2) tuples
        """
        pass

    @abstractmethod
    def get_player_by_index(self, game_state: Any, index: int) -> Any:
        """
        Get a player state by index (0 or 1)

        Args:
            game_state: Current game state
            index: Player index (0 for first player, 1 for second)

        Returns:
            Player state object
        """
        pass

    @abstractmethod
    def get_opponent(self, game_state: Any, player_state: Any) -> Any:
        """
        Get the opponent's state given a player's state

        Args:
            game_state: Current game state
            player_state: State of the player whose opponent we want

        Returns:
            Opponent's player state
        """
        pass

    @abstractmethod
    def update_emotional_state(self, player_state: Any, decision: Dict[str, Any], opponent: Any) -> None:
        """
        Update a player's emotional/psychological state

        Args:
            player_state: Player whose emotion to update
            decision: The decision that was made (with metrics)
            opponent: The opponent's state
        """
        pass

    @abstractmethod
    def record_turn_metrics(self, game_state: Any, player1_decision: Dict, player2_decision: Dict) -> None:
        """
        Record psychological metrics for analysis

        Args:
            game_state: Current game state
            player1_decision: First player's decision with metrics
            player2_decision: Second player's decision with metrics
        """
        pass

    @abstractmethod
    def get_max_turns(self) -> int:
        """Return maximum number of turns for safety limit"""
        pass

    @abstractmethod
    def format_persona_for_summary(self, persona: Any) -> str:
        """
        Format a persona for inclusion in summary reports

        Args:
            persona: Persona object

        Returns:
            String representation for reports
        """
        pass
