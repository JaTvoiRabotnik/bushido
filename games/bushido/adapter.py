from typing import Any, List, Dict, Optional
import re
import logging
from google.adk.tools import FunctionTool

from framework.adapter import GameAgentAdapter
from .models import PlayerState, GameState, BushidoDecision, ActionCard, PersonalityTrait
from .tools import get_game_situation, get_available_actions, get_technique_details
from .metrics import MetricsTracker

logger = logging.getLogger(__name__)

class BushidoAdapter(GameAgentAdapter):
    """
    Bushido-specific implementation of the GameAgentAdapter.
    Handles prompt generation, tool creation, and response parsing.
    """

    def get_system_instruction(self, player_state: PlayerState) -> str:
        """Get the system instruction for the agent based on player state"""
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

    def get_tools(self, player_state: PlayerState, game_state: GameState) -> List[FunctionTool]:
        """Get the tools available to the agent"""
        
        # Create closures that bind the state to the stateless functions
        # We define them with the correct names so FunctionTool can pick them up
        
        def get_game_situation_tool() -> str:
            """
            Get the current game situation including your stats, opponent stats, and position.
            Returns a detailed description of the current game state.
            """
            return get_game_situation(player_state, game_state)
            
        def get_available_actions_tool() -> str:
            """
            Get list of available action combinations you can take this turn.
            Returns all possible action combinations based on current position and game rules.
            """
            return get_available_actions(player_state, game_state)
            
        # Rename for tool usage
        get_game_situation_tool.__name__ = "get_game_situation"
        get_available_actions_tool.__name__ = "get_available_actions"
        
        return [
            FunctionTool(get_game_situation_tool),
            FunctionTool(get_available_actions_tool),
            FunctionTool(get_technique_details)
        ]

    def parse_response(self, response: str, player_state: PlayerState, game_state: GameState) -> Dict[str, Any]:
        """Parse the agent's response into a game decision"""
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

        # Validate with Pydantic model (optional but good for structure)
        # We construct the dict first, then could validate if needed
        # decision_model = BushidoDecision(
        #     actions=actions,
        #     technique=technique,
        #     reasoning=reasoning,
        #     emotional_state=player_state.persona.emotional_state
        # )

        return {
            "actions": actions_tuple,
            "technique": technique,
            "reasoning": reasoning,
            "deliberation": response,  # Full reasoning response
            **metrics
        }

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
