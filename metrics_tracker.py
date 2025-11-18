"""
Metrics and psychological state tracking for Bushido Card Game
Handles tension, enjoyment, and emotional state calculations
"""

from typing import Tuple, Dict
from models import PlayerState, GameState, ActionCard, PersonalityTrait


class MetricsTracker:
    """
    Centralized metrics and player psychology tracking
    Extracted from scattered calculations in original code
    """

    @staticmethod
    def calculate_tension(player_state: PlayerState, game_state: GameState) -> float:
        """
        Calculate current tension level for a player
        Extracted from original _calculate_tension (lines 638-642)
        """
        health_pressure = 1.0 - (player_state.health / 3.0)
        turn_pressure = min(game_state.turn_number / 5.0, 1.0)
        return (health_pressure + turn_pressure) / 2

    @staticmethod
    def calculate_enjoyment(
        player_state: PlayerState,
        actions: Tuple[ActionCard, ...]
    ) -> float:
        """
        Calculate expected enjoyment from action
        Extracted from original _calculate_enjoyment (lines 644-655)
        """
        enjoyment = 0.5

        if player_state.persona.personality == PersonalityTrait.AGGRESSIVE:
            if ActionCard.ATTACK in actions:
                enjoyment += 0.3
        elif player_state.persona.personality == PersonalityTrait.DEFENSIVE:
            if ActionCard.DEFEND in actions:
                enjoyment += 0.3

        return min(enjoyment, 1.0)

    @staticmethod
    def update_emotional_state(
        player_state: PlayerState,
        observations: Dict
    ) -> None:
        """
        Update emotional state based on game situation
        Extracted from original _update_emotional_state (lines 657-675)
        """
        tension = observations["tension_level"]

        if player_state.health == 1:
            player_state.persona.emotional_state = "desperate"
            player_state.persona.confidence_level *= 0.7
        elif tension > player_state.persona.tension_threshold:
            player_state.persona.emotional_state = "tense"
            player_state.persona.confidence_level *= 0.9
        elif observations["opponent_health"] == 1:
            player_state.persona.emotional_state = "excited"
            player_state.persona.confidence_level *= 1.2
        else:
            player_state.persona.emotional_state = "focused"

        # Clamp confidence
        player_state.persona.confidence_level = max(
            0.1,
            min(1.0, player_state.persona.confidence_level)
        )

    @staticmethod
    def record_turn_metrics(
        game_state: GameState,
        challenger_decision: Dict,
        defender_decision: Dict
    ) -> None:
        """
        Record psychological metrics for a turn
        Extracted from original run_turn (lines 790-799)
        """
        game_state.tension_levels.append(
            (challenger_decision["tension"] + defender_decision["tension"]) / 2
        )
        game_state.choice_difficulty.append(
            (challenger_decision["choice_difficulty"] +
             defender_decision["choice_difficulty"]) / 2
        )
        game_state.enjoyment_scores.append(
            (challenger_decision["enjoyment"] + defender_decision["enjoyment"]) / 2
        )

    @staticmethod
    def calculate_decision_metrics(
        player_state: PlayerState,
        game_state: GameState,
        actions: Tuple[ActionCard, ...]
    ) -> Dict[str, float]:
        """
        Calculate all metrics for a decision
        Consolidates scattered metric calculations
        """
        tension = MetricsTracker.calculate_tension(player_state, game_state)
        enjoyment = MetricsTracker.calculate_enjoyment(player_state, actions)
        choice_difficulty = 0.5  # Could be enhanced with more analysis

        return {
            "tension": tension,
            "enjoyment": enjoyment,
            "choice_difficulty": choice_difficulty
        }
