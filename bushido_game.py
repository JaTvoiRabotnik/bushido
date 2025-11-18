"""
Bushido Card Game Implementation
Implements GameInterface for the Bushido card duel game
"""

import re
import random
import logging
from typing import List, Dict, Any, Tuple
from uuid import uuid4

from google.adk.tools import FunctionTool

from game_interface import GameInterface
from models import (
    Position, ActionCard, PlayerRole, PersonalityTrait,
    PlayerPersona, PlayerState, GameState
)
from constants import TECHNIQUE_CARDS, MAX_TURNS, HONOR_RESTRICTION_TURN
from resource_manager import PlayerResourceManager
from rules_engine import GameRulesEngine
from metrics_tracker import MetricsTracker


logger = logging.getLogger(__name__)


class BushidoGame(GameInterface):
    """Bushido Card Game implementation of the game interface"""

    def get_game_name(self) -> str:
        """Return the name of the game"""
        return "Bushido Card Game"

    def get_game_description(self) -> str:
        """Return a description of the game for display purposes"""
        return "A tactical samurai card duel game with positioning, resources, and technique cards"

    def create_player_tools(self, player_state: PlayerState, game_state: GameState) -> List[FunctionTool]:
        """Create game-specific tools for the AI agent"""

        def get_game_situation() -> str:
            """
            Get the current game situation including your stats, opponent stats, and position.
            Returns a detailed description of the current game state.
            """
            opponent = self.get_opponent(game_state, player_state)

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
                    situation += f"  Turn {turn['turn']}: {[a.value if hasattr(a, 'value') else a for a in opp_actions]}\n"

            return situation

        def get_available_actions() -> str:
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

        return [
            FunctionTool(get_game_situation),
            FunctionTool(get_available_actions),
            FunctionTool(get_technique_details)
        ]

    def get_agent_instruction(self, player_state: PlayerState) -> str:
        """Get the main instruction prompt for the AI agent"""

        persona_instructions = self.get_persona_instructions(player_state.persona.personality)

        return f"""
You are playing a tactical samurai card duel game as {player_state.persona.name}.
Your personality: {player_state.persona.personality.value}
Risk tolerance: {player_state.persona.risk_tolerance:.2f}

THINK LIKE A HUMAN PLAYER:
1. Consider your emotions and how they affect your choices
2. Remember what worked and didn't work in previous turns
3. Try to read your opponent's patterns and intentions
4. Balance between optimal play and your personality tendencies
5. Express internal tension when making difficult choices

{persona_instructions}

DECISION-MAKING PROCESS:
1. First, call get_game_situation() to understand the current state
2. Call get_available_actions() to see your options
3. Reason through the tactical situation considering your personality
4. Express your internal monologue (doubts, hopes, excitement, fear)
5. Make your final decision

OUTPUT FORMAT:
After your analysis, provide your decision in this exact format:
DECISION: [action1, action2, ...]
TECHNIQUE: [technique name or "None"]
REASONING: [your reasoning in 1-2 sentences]

Examples:
DECISION: [Advance, Attack]
TECHNIQUE: Tsubame Gaeshi
REASONING: I need to press the advantage while I have momentum. Time to strike!

DECISION: [Defend]
TECHNIQUE: Mizu no Kokoro
REASONING: They're getting aggressive, better protect myself and build balance.
"""

    def get_persona_instructions(self, personality: PersonalityTrait) -> str:
        """Get personality-specific playing instructions"""

        instructions = {
            PersonalityTrait.AGGRESSIVE: """
Focus on:
- Pushing forward and maintaining pressure
- Taking calculated risks for big damage
- Feeling frustrated when forced to defend
- Getting excited when you have momentum
""",
            PersonalityTrait.DEFENSIVE: """
Focus on:
- Protecting yourself and minimizing damage
- Waiting for the perfect opportunity
- Feeling anxious when health is low
- Finding satisfaction in successful blocks
""",
            PersonalityTrait.ADAPTIVE: """
Focus on:
- Reading opponent patterns and adjusting
- Switching between offensive and defensive
- Feeling curious about opponent's strategy
- Enjoying the mental chess match
""",
            PersonalityTrait.CALCULATED: """
Focus on:
- Mathematical optimization of choices
- Resource management and efficiency
- Feeling satisfied by perfect plays
- Getting annoyed by forced suboptimal moves
""",
            PersonalityTrait.UNPREDICTABLE: """
Focus on:
- Keeping the opponent guessing
- Mixing up patterns intentionally
- Enjoying the chaos and confusion
- Feeling clever when bluffs work
""",
            PersonalityTrait.HONORABLE: """
Focus on:
- Making stylish and dramatic plays
- Avoiding "cheap" tactics
- Feeling proud of bold moves
- Respecting worthy opponents
"""
        }

        return instructions.get(personality, "")

    def parse_decision(self, response: str, player_state: PlayerState, game_state: GameState) -> Dict[str, Any]:
        """Parse the AI agent's response into a game decision"""
        # Default values
        actions = []
        technique = None
        reasoning = "Decision made based on tactical analysis"

        # Extract DECISION line
        decision_match = re.search(r'DECISION:\s*\[(.*?)\]', response, re.IGNORECASE)
        if decision_match:
            action_str = decision_match.group(1)
            # Parse action names
            action_names = [a.strip().strip('"').strip("'") for a in action_str.split(',')]
            for action_name in action_names:
                if action_name:
                    try:
                        # Match action by name
                        for action in ActionCard:
                            if action.value.lower() == action_name.lower():
                                actions.append(action)
                                break
                    except:
                        logger.warning(f"Could not parse action: {action_name}")

        # Extract TECHNIQUE line
        technique_match = re.search(r'TECHNIQUE:\s*([^\n]+)', response, re.IGNORECASE)
        if technique_match:
            tech_name = technique_match.group(1).strip()
            if tech_name.lower() not in ['none', 'n/a', '']:
                technique = tech_name

        # Extract REASONING line
        reasoning_match = re.search(r'REASONING:\s*([^\n]+)', response, re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()

        # Convert actions to tuple
        actions_tuple = tuple(actions)

        # Calculate metrics for this decision using MetricsTracker
        metrics = MetricsTracker.calculate_decision_metrics(
            player_state, game_state, actions_tuple
        )

        return {
            "actions": actions_tuple,
            "technique": technique,
            "reasoning": reasoning,
            "deliberation": response,  # Full reasoning response
            **metrics
        }

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
