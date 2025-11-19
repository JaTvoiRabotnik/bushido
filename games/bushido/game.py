import logging
import random
from typing import List, Dict, Any, Tuple
from uuid import uuid4

from google.adk.tools import FunctionTool

from framework.interface import GameInterface
from .models import (
    Position, ActionCard, PlayerRole, PersonalityTrait,
    PlayerPersona, PlayerState, GameState
)
from .constants import TECHNIQUE_CARDS, MAX_TURNS
from .resources import PlayerResourceManager
from .rules import GameRulesEngine
from .metrics import MetricsTracker
from .adapter import BushidoAdapter

logger = logging.getLogger(__name__)

class BushidoGame(GameInterface):
    """Bushido Card Game implementation of the game interface"""

    def __init__(self):
        self.adapter = BushidoAdapter()

    def get_game_name(self) -> str:
        """Return the name of the game"""
        return "Bushido Card Game"

    def get_game_description(self) -> str:
        """Return a description of the game for display purposes"""
        return "A tactical samurai card duel game with positioning, resources, and technique cards"

    def create_player_tools(self, player_state: PlayerState, game_state: GameState) -> List[FunctionTool]:
        """Create game-specific tools for the AI agent"""
        return self.adapter.get_tools(player_state, game_state)

    def get_agent_instruction(self, player_state: PlayerState) -> str:
        """Get the main instruction prompt for the AI agent"""
        return self.adapter.get_system_instruction(player_state)

    def get_persona_instructions(self, personality: PersonalityTrait) -> str:
        """Get personality-specific playing instructions"""
        return self.adapter.get_persona_instructions(personality)

    def parse_decision(self, response: str, player_state: PlayerState, game_state: GameState) -> Dict[str, Any]:
        """Parse the AI agent's response into a game decision"""
        return self.adapter.parse_response(response, player_state, game_state)

    def initialize_players(self, personas: Tuple[PlayerPersona, PlayerPersona], game_id: str) -> Tuple[PlayerState, PlayerState]:
        """Initialize player states for a new game"""

        # Initialize challenger
        challenger = PlayerState(
            role=PlayerRole.CHALLENGER,
            persona=personas[0],
            momentum=1,  # Challenger starts with momentum
            balance=0
        )

        # Initialize defender
        defender = PlayerState(
            role=PlayerRole.DEFENDER,
            persona=personas[1],
            momentum=0,
            balance=1  # Defender starts with balance
        )

        # Assign technique cards
        self._assign_techniques(challenger, defender)

        return challenger, defender

    def _assign_techniques(self, challenger: PlayerState, defender: PlayerState):
        """Assign technique cards to players"""
        available_techniques = list(TECHNIQUE_CARDS.keys())
        random.shuffle(available_techniques)

        # Remove one random card
        available_techniques.pop()

        # Draft process as per rules
        challenger.technique_cards = [
            available_techniques[0],
            available_techniques[2]
        ]
        defender.technique_cards = [
            available_techniques[1],
            available_techniques[3]
        ]

    def initialize_game_state(self, game_id: str, player1: PlayerState, player2: PlayerState) -> GameState:
        """Initialize the game state"""
        game_state = GameState(
            game_id=game_id,
            position=Position.APART,
            challenger=player1,
            defender=player2
        )
        return game_state

    def resolve_turn(
        self,
        game_state: GameState,
        player1_decision: Dict[str, Any],
        player2_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a turn given both players' decisions"""

        # Use the GameRulesEngine to resolve turn
        turn_result, new_position = GameRulesEngine.resolve_turn(
            game_state.turn_number,
            game_state.position,
            game_state.challenger,
            game_state.defender,
            player1_decision,
            player2_decision
        )

        # Store the new position in the result for update_game_state
        turn_result["new_position"] = new_position

        return turn_result

    def update_game_state(self, game_state: GameState, turn_result: Dict[str, Any]) -> None:
        """Update the game state after turn resolution"""

        # Update position
        game_state.position = turn_result["new_position"]

        # Update player resources using PlayerResourceManager
        PlayerResourceManager.update_both_players(
            game_state.challenger,
            game_state.defender,
            turn_result["challenger_actions"],
            turn_result["defender_actions"],
            turn_result["damage_dealt"]
        )

        # Store turn in history
        game_state.turn_history.append(turn_result)

    def check_victory(self, game_state: GameState) -> str:
        """Check if the game has ended and who won"""
        last_turn = game_state.turn_history[-1] if game_state.turn_history else None
        return GameRulesEngine.check_victory(
            game_state.challenger,
            game_state.defender,
            last_turn
        )

    def get_game_summary(self, game_state: GameState, winner: str) -> Dict[str, Any]:
        """Generate a summary of the completed game"""
        return {
            "game_id": game_state.game_id,
            "winner": winner,
            "total_turns": game_state.turn_number,
            "final_health": {
                "challenger": game_state.challenger.health,
                "defender": game_state.defender.health
            },
            "average_tension": sum(game_state.tension_levels) / len(game_state.tension_levels) if game_state.tension_levels else 0,
            "average_choice_difficulty": sum(game_state.choice_difficulty) / len(game_state.choice_difficulty) if game_state.choice_difficulty else 0,
            "average_enjoyment": sum(game_state.enjoyment_scores) / len(game_state.enjoyment_scores) if game_state.enjoyment_scores else 0,
            "turn_history": game_state.turn_history
        }

    def generate_persona_pairs(self, count: int) -> List[Tuple[PlayerPersona, PlayerPersona]]:
        """Generate diverse persona pairs for testing"""
        pairs = []
        personalities = list(PersonalityTrait)

        for i in range(count):
            # Create diverse matchups
            p1_personality = random.choice(personalities)
            p2_personality = random.choice(personalities)

            p1 = PlayerPersona(
                name=f"Player_{i}_A",
                personality=p1_personality,
                risk_tolerance=random.uniform(0.2, 0.9),
                tension_threshold=random.uniform(0.5, 0.9)
            )

            p2 = PlayerPersona(
                name=f"Player_{i}_B",
                personality=p2_personality,
                risk_tolerance=random.uniform(0.2, 0.9),
                tension_threshold=random.uniform(0.5, 0.9)
            )

            pairs.append((p1, p2))

        return pairs

    def get_player_by_index(self, game_state: GameState, index: int) -> PlayerState:
        """Get a player state by index (0 or 1)"""
        return game_state.challenger if index == 0 else game_state.defender

    def get_opponent(self, game_state: GameState, player_state: PlayerState) -> PlayerState:
        """Get the opponent's state given a player's state"""
        return (game_state.defender
                if player_state.role == PlayerRole.CHALLENGER
                else game_state.challenger)

    def update_emotional_state(self, player_state: PlayerState, decision: Dict[str, Any], opponent: PlayerState) -> None:
        """Update a player's emotional/psychological state"""
        observations = {
            "tension_level": decision["tension"],
            "opponent_health": opponent.health
        }
        MetricsTracker.update_emotional_state(player_state, observations)

    def record_turn_metrics(self, game_state: GameState, player1_decision: Dict, player2_decision: Dict) -> None:
        """Record psychological metrics for analysis"""
        MetricsTracker.record_turn_metrics(
            game_state,
            player1_decision,
            player2_decision
        )

    def get_max_turns(self) -> int:
        """Return maximum number of turns for safety limit"""
        return MAX_TURNS

    def format_persona_for_summary(self, persona: PlayerPersona) -> str:
        """Format a persona for inclusion in summary reports"""
        return persona.personality.value
