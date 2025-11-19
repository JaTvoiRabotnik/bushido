from typing import Dict, Any, List, Optional
from .models import PlayerState, GameState, PlayerRole, ActionCard
from .constants import TECHNIQUE_CARDS, HONOR_RESTRICTION_TURN

def get_opponent(game_state: GameState, player_state: PlayerState) -> PlayerState:
    """Helper to get opponent state"""
    return (game_state.defender
            if player_state.role == PlayerRole.CHALLENGER
            else game_state.challenger)

def get_game_situation(player_state: PlayerState, game_state: GameState) -> str:
    """
    Get the current game situation including your stats, opponent stats, and position.
    Returns a detailed description of the current game state.
    """
    opponent = get_opponent(game_state, player_state)

    situation = f"""
CURRENT GAME STATE (Turn {game_state.turn_number}):

YOUR STATUS:
- Health: {player_state.health}/3
- Momentum: {player_state.momentum}/3
- Balance: {player_state.balance}/3
- Emotional State: {player_state.persona.emotional_state}
- Confidence: {player_state.persona.confidence_level:.2f}

OPPONENT STATUS:
- Health: {opponent.health}/3
- Momentum: {opponent.momentum}/3
- Balance: {opponent.balance}/3

POSITION: {game_state.position.value}

YOUR TECHNIQUE CARDS:
{', '.join(player_state.technique_cards)}

YOUR PERSONALITY: {player_state.persona.personality.value}
Risk Tolerance: {player_state.persona.risk_tolerance:.2f}
"""

    # Add pattern recognition
    if len(game_state.turn_history) >= 2:
        recent_turns = game_state.turn_history[-2:]
        situation += "\nRECENT OPPONENT ACTIONS:\n"
        for turn in recent_turns:
            opp_actions = turn.get("defender_actions" if player_state.role == PlayerRole.CHALLENGER
                                  else "challenger_actions", [])
            # Handle both enum objects and string values if they were serialized
            actions_str = []
            for a in opp_actions:
                if hasattr(a, 'value'):
                    actions_str.append(a.value)
                else:
                    actions_str.append(str(a))
            
            situation += f"  Turn {turn['turn']}: {actions_str}\n"

    return situation

def get_available_actions(player_state: PlayerState, game_state: GameState) -> str:
    """
    Get list of available action combinations you can take this turn.
    Returns all possible action combinations based on current position and game rules.
    """
    position = game_state.position
    turn = game_state.turn_number

    actions_desc = f"""
AVAILABLE ACTIONS (at {position.value}):

BASIC ACTIONS:
- Attack (deal damage based on your Strength + position bonus)
- Defend (reduce incoming damage by your Defense)
- Insight (learn about opponent's hidden attributes)

MOVEMENT:
- Stay (gain 1 Balance)
- Advance (move closer, gain Momentum, lose Balance)
- Retreat{"" if turn <= HONOR_RESTRICTION_TURN else " (FORBIDDEN after turn 3 - honor violation!)"}

COMBINATION PLAYS:

- Stay + Attack (standard strike)
- Stay + Defend (hold position)
- Stay + Insight (observe opponent)
- Advance + Attack (aggressive rush)
- Advance + Defend (cautious advance)
- Advance + Insight (probe opponent)
- Retreat + Attack (hit and run){"" if turn <= HONOR_RESTRICTION_TURN else " (ONLY if turn <= 3)"}
- Retreat + Defend (full defense){"" if turn <= HONOR_RESTRICTION_TURN else " (ONLY if turn <= 3)"}
- Retreat + Insight (fall back and observe){"" if turn <= HONOR_RESTRICTION_TURN else " (ONLY if turn <= 3)"}

RESOURCES:
- Momentum helps with aggressive techniques
- Balance helps with defensive techniques
- Some techniques require specific resources to use or evade

Remember: You must choose actions that fit your personality ({player_state.persona.personality.value})
but also make tactical sense!
"""
    return actions_desc

def get_technique_details(technique_name: str) -> str:
    """
    Get detailed information about a specific technique card.

    Args:
        technique_name: Name of the technique to look up

    Returns:
        Detailed description of the technique's effects and requirements
    """
    if technique_name not in TECHNIQUE_CARDS:
        return f"Technique '{technique_name}' not found. Available techniques: {', '.join(TECHNIQUE_CARDS.keys())}"

    tech = TECHNIQUE_CARDS[technique_name]
    return f"""
TECHNIQUE: {technique_name}
Type: {tech['type']}
Description: {tech['description']}

Effects:
- Attack/Defense: {tech.get('attack_effect') or tech.get('defense_effect') or tech.get('attack_defense_effect', 'N/A')}
- Evade Cost: {tech['evade_cost']}
- Special: {tech['special']}
"""
