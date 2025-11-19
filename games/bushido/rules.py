import copy
from typing import Tuple, Dict, Any, Optional
from .models import Position, ActionCard, PlayerState, PlayerRole, GameState
from .constants import HONOR_RESTRICTION_TURN
from .resources import PlayerResourceManager

class GameRulesEngine:
    """
    Centralized game rules and mechanics
    """

    @staticmethod
    def resolve_position(
        current_pos: Position,
        challenger_actions: Tuple[ActionCard, ...],
        defender_actions: Tuple[ActionCard, ...]
    ) -> Position:
        """
        Resolve position changes based on player movements
        """
        # Extract movement actions
        challenger_move = None
        defender_move = None

        for action in challenger_actions:
            if action in [ActionCard.ADVANCE, ActionCard.RETREAT]:
                challenger_move = action
                break

        for action in defender_actions:
            if action in [ActionCard.ADVANCE, ActionCard.RETREAT]:
                defender_move = action
                break

        # Apply position logic from rules
        if current_pos == Position.APART:
            if challenger_move == ActionCard.ADVANCE or defender_move == ActionCard.ADVANCE:
                if challenger_move != ActionCard.RETREAT and defender_move != ActionCard.RETREAT:
                    return Position.SWORD

        elif current_pos == Position.SWORD:
            if challenger_move == ActionCard.ADVANCE and defender_move == ActionCard.ADVANCE:
                return Position.CLOSE
            elif challenger_move == ActionCard.ADVANCE and defender_move != ActionCard.RETREAT:
                return Position.CLOSE
            elif defender_move == ActionCard.ADVANCE and challenger_move != ActionCard.RETREAT:
                return Position.CLOSE
            elif challenger_move == ActionCard.RETREAT and defender_move == ActionCard.RETREAT:
                return Position.APART
            elif challenger_move == ActionCard.RETREAT or defender_move == ActionCard.RETREAT:
                return Position.APART

        elif current_pos == Position.CLOSE:
            if challenger_move == ActionCard.RETREAT and defender_move == ActionCard.RETREAT:
                return Position.APART
            elif challenger_move == ActionCard.RETREAT and defender_move != ActionCard.ADVANCE:
                return Position.SWORD
            elif defender_move == ActionCard.RETREAT and challenger_move != ActionCard.ADVANCE:
                return Position.SWORD

        return current_pos

    @staticmethod
    def calculate_attack_value(
        player: PlayerState,
        actions: Tuple[ActionCard, ...],
        position: Position
    ) -> int:
        """
        Calculate total attack value for a player
        """
        attack_total = player.strength

        if ActionCard.ADVANCE in actions:
            attack_total += 1

        if position == Position.CLOSE:
            attack_total += 1

        return attack_total

    @staticmethod
    def calculate_defense_value(
        player: PlayerState,
        actions: Tuple[ActionCard, ...]
    ) -> int:
        """
        Calculate total defense value for a player
        """
        if ActionCard.DEFEND not in actions:
            return 0

        defense_total = player.defense

        if ActionCard.RETREAT in actions:
            defense_total += 1

        return defense_total

    @staticmethod
    def resolve_combat(
        challenger: PlayerState,
        defender: PlayerState,
        challenger_actions: Tuple[ActionCard, ...],
        defender_actions: Tuple[ActionCard, ...],
        position: Position
    ) -> Dict[str, int]:
        """
        Resolve combat exchanges between players
        """
        damage = {"challenger": 0, "defender": 0}

        # Check for attacks
        challenger_attacking = ActionCard.ATTACK in challenger_actions
        defender_attacking = ActionCard.ATTACK in defender_actions

        if not (challenger_attacking or defender_attacking):
            return damage

        # Resolve challenger's attack
        if challenger_attacking:
            attack_total = GameRulesEngine.calculate_attack_value(
                challenger, challenger_actions, position
            )
            defense_total = GameRulesEngine.calculate_defense_value(
                defender, defender_actions
            )
            damage["defender"] = max(0, attack_total - defense_total)

        # Resolve defender's attack
        if defender_attacking:
            attack_total = GameRulesEngine.calculate_attack_value(
                defender, defender_actions, position
            )
            defense_total = GameRulesEngine.calculate_defense_value(
                challenger, challenger_actions
            )
            damage["challenger"] = max(0, attack_total - defense_total)

        return damage

    @staticmethod
    def check_honor_violation(
        turn_number: int,
        actions: Tuple[ActionCard, ...]
    ) -> bool:
        """
        Check if actions violate honor rules
        After turn 3, retreating is forbidden
        """
        if turn_number > HONOR_RESTRICTION_TURN:
            return ActionCard.RETREAT in actions
        return False

    @staticmethod
    def resolve_turn(
        turn_number: int,
        position: Position,
        challenger: PlayerState,
        defender: PlayerState,
        challenger_decision: Dict[str, Any],
        defender_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete turn resolution using all rules
        """
        challenger_actions = challenger_decision["actions"]
        defender_actions = defender_decision["actions"]

        result = {
            "turn": turn_number,
            "challenger_actions": challenger_actions,
            "defender_actions": defender_actions,
            "challenger_technique": challenger_decision["technique"],
            "defender_technique": defender_decision["technique"],
            "position_before": position.value,
            "damage_dealt": {"challenger": 0, "defender": 0}
        }

        # Resolve position changes
        new_position = GameRulesEngine.resolve_position(
            position, challenger_actions, defender_actions
        )
        result["position_after"] = new_position.value

        # Resolve combat if applicable
        if new_position != Position.APART:
            damage = GameRulesEngine.resolve_combat(
                challenger, defender,
                challenger_actions, defender_actions,
                new_position
            )
            result["damage_dealt"] = damage

        # Check for honor violations
        if GameRulesEngine.check_honor_violation(turn_number, challenger_actions):
            result["honor_violation"] = "Challenger"
        if GameRulesEngine.check_honor_violation(turn_number, defender_actions):
            result["honor_violation"] = "Defender"

        return result, new_position

    @staticmethod
    def check_victory(
        challenger: PlayerState,
        defender: PlayerState,
        last_turn: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Check for victory conditions
        """
        # Check health-based victory
        if challenger.health <= 0 and defender.health <= 0:
            return "DRAW"
        elif challenger.health <= 0:
            return "DEFENDER"
        elif defender.health <= 0:
            return "CHALLENGER"

        # Check for honor violation
        if last_turn and "honor_violation" in last_turn:
            if last_turn["honor_violation"] == "Challenger":
                return "DEFENDER"
            elif last_turn["honor_violation"] == "Defender":
                return "CHALLENGER"

        return None

    @staticmethod
    def get_next_state(current_state: GameState, challenger_decision: Dict[str, Any], defender_decision: Dict[str, Any]) -> GameState:
        """
        Simulate the next state given the current state and player decisions.
        Returns a new GameState object without modifying the original.
        """
        # Create a deep copy of the state to avoid mutation
        next_state = copy.deepcopy(current_state)

        # Resolve turn
        turn_result, new_position = GameRulesEngine.resolve_turn(
            next_state.turn_number + 1,
            next_state.position,
            next_state.challenger,
            next_state.defender,
            challenger_decision,
            defender_decision
        )

        # Update state
        next_state.turn_number += 1
        next_state.position = new_position

        # Update player resources
        PlayerResourceManager.update_both_players(
            next_state.challenger,
            next_state.defender,
            turn_result["challenger_actions"],
            turn_result["defender_actions"],
            turn_result["damage_dealt"]
        )

        # Append to history
        next_state.turn_history.append(turn_result)

        return next_state
