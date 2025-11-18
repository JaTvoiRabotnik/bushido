"""
Bushido Card Game Testing Agent System
Using Google ADK for multi-agent game simulation with human-like reasoning

Based on patterns from "Agentic Design Patterns" book:
- Chapter 3: Parallelization (page 32) - for running multiple game simulations
- Chapter 17: Reasoning Techniques (page 241) - for player decision-making
- Chapter 20: Prioritization (page 310) - for strategic choices
- Memory patterns for adaptive strategy
"""

import asyncio
import json
import logging
import random
import re
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import uuid
from pathlib import Path

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types
import vertexai
from vertexai.generative_models import GenerativeModel

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bushido_simulation.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Environment configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
VERTEX_AI_INITIALIZED = False

# ==================== INITIALIZATION ====================

def initialize_vertex_ai():
    """Initialize Vertex AI with error handling"""
    global VERTEX_AI_INITIALIZED

    if VERTEX_AI_INITIALIZED:
        return True

    if not PROJECT_ID:
        logger.warning("GOOGLE_CLOUD_PROJECT not set. Set environment variable for production use.")
        logger.warning("Running in test mode without Vertex AI.")
        return False

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        VERTEX_AI_INITIALIZED = True
        logger.info(f"Vertex AI initialized: project={PROJECT_ID}, location={LOCATION}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        logger.warning("Running in test mode without Vertex AI.")
        return False

# ==================== GAME CONSTANTS ====================

class Position(Enum):
    APART = "Apart"
    SWORD = "Sword Range"
    CLOSE = "Close Combat"

class ActionCard(Enum):
    ATTACK = "Attack"
    DEFEND = "Defend"
    ADVANCE = "Advance"
    RETREAT = "Retreat"
    INSIGHT = "Insight"

class PlayerRole(Enum):
    CHALLENGER = "Challenger"
    DEFENDER = "Defender"

# Technique cards as defined in the rules
TECHNIQUE_CARDS = {
    "Tsubame Gaeshi": {
        "type": "Aggressive Momentum",
        "description": "Lightning-fast double strike",
        "attack_effect": "+1 Attack per Momentum",
        "evade_cost": "3 Momentum",
        "special": "At Close Combat, bypass defense with 3 Momentum"
    },
    "Mizu no Kokoro": {
        "type": "Defensive Balance",
        "description": "Perfect defensive stillness",
        "defense_effect": "+1 Defense per Balance",
        "evade_cost": "3 Balance",
        "special": "At Sword Range, bypass evasion with 3 Balance"
    },
    "Kuzushi": {
        "type": "Aggressive Disruption",
        "description": "Disrupts opponent's stance",
        "attack_effect": "+2 Attack when Advancing",
        "evade_cost": "3 Balance",
        "special": "Steal 1 Balance on hit"
    },
    "Ai-Uchi": {
        "type": "Sacrificial",
        "description": "Mutual destruction technique",
        "attack_effect": "Ignore all Defense and Evades",
        "evade_cost": "Cannot evade",
        "special": "Cannot defend when using"
    },
    "Irimi": {
        "type": "Close Combat Specialist",
        "description": "Step inside opponent's reach",
        "movement_effect": "+2 Balance when Advancing to Close",
        "evade_cost": "2 Momentum at Close Combat",
        "special": "Halve opponent's Momentum bonuses at Close"
    },
    "Ma-ai": {
        "type": "Range Control",
        "description": "Masterful spacing control",
        "defense_effect": "+2 Defense when Retreating",
        "evade_cost": "1 Balance at Sword Range or further",
        "special": "Lose only 1 Momentum when Retreating"
    },
    "Mushin": {
        "type": "Zen Emptiness",
        "description": "Power through emptiness",
        "attack_defense_effect": "+3 if 0 Momentum AND 0 Balance",
        "evade_cost": "Free if 0 Momentum and 0 Balance",
        "special": "Can reset both resources to 0"
    },
    "Nagashi": {
        "type": "Counter-fighter",
        "description": "Redirect opponent's force",
        "defense_effect": "+1 Defense, gain Momentum from damage prevented",
        "evade_cost": "2 Momentum to evade and gain 1 Balance",
        "special": "Counter for 2 damage if opponent attacks with 5+"
    }
}

# ==================== PLAYER PERSONAS ====================

class PersonalityTrait(Enum):
    """Based on book's emphasis on persona-based agents (page 372)"""
    AGGRESSIVE = "Aggressive - Prefers offensive tactics"
    DEFENSIVE = "Defensive - Prioritizes survival"
    ADAPTIVE = "Adaptive - Changes strategy based on opponent"
    CALCULATED = "Calculated - Focuses on optimal plays"
    UNPREDICTABLE = "Unpredictable - Varies tactics to confuse"
    HONORABLE = "Honorable - Values style over pure victory"

@dataclass
class PlayerPersona:
    """Human-like persona for believable simulation"""
    name: str
    personality: PersonalityTrait
    risk_tolerance: float  # 0.0 (cautious) to 1.0 (reckless)
    learning_rate: float  # How quickly they adapt
    emotional_state: str = "calm"
    confidence_level: float = 0.5
    
    # Psychological factors
    tension_threshold: float = 0.7  # When they feel pressure
    enjoyment_factors: List[str] = field(default_factory=list)
    
    def describe(self) -> str:
        """Generate a human-like internal monologue"""
        return f"{self.name} ({self.personality.value}): {self.emotional_state}, confidence: {self.confidence_level:.2f}"

# ==================== GAME STATE ====================

@dataclass
class PlayerState:
    """Complete state of a player"""
    role: PlayerRole
    persona: PlayerPersona
    health: int = 3
    momentum: int = 0
    balance: int = 0
    
    # Hidden attributes (sum to 6)
    speed: int = 2
    strength: int = 2
    defense: int = 2
    
    # Cards and techniques
    action_cards: List[ActionCard] = field(default_factory=list)
    technique_cards: List[str] = field(default_factory=list)
    current_technique: Optional[str] = None
    
    # Knowledge about opponent
    known_attributes: Dict[str, Optional[int]] = field(default_factory=dict)
    
    # Strategy memory
    strategy_log: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.action_cards:
            self.action_cards = list(ActionCard)
        if not self.known_attributes:
            self.known_attributes = {"speed": None, "strength": None, "defense": None}

@dataclass
class GameState:
    """Complete game state"""
    game_id: str
    turn_number: int = 0
    position: Position = Position.APART
    
    # Players
    challenger: PlayerState = None
    defender: PlayerState = None
    
    # History for analysis
    turn_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics for evaluation
    tension_levels: List[float] = field(default_factory=list)
    choice_difficulty: List[float] = field(default_factory=list)
    enjoyment_scores: List[float] = field(default_factory=list)
    
    def get_player(self, role: PlayerRole) -> PlayerState:
        return self.challenger if role == PlayerRole.CHALLENGER else self.defender

# ==================== TOOL FUNCTIONS ====================

def create_player_tools(player_state: PlayerState, game_state: GameState):
    """Create tool functions with access to player and game state via closures"""

    def get_game_situation() -> str:
        """
        Get the current game situation including your stats, opponent stats, and position.
        Returns a detailed description of the current game state.
        """
        opponent = (game_state.defender
                   if player_state.role == PlayerRole.CHALLENGER
                   else game_state.challenger)

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
- Stay (gain 1 Balance)
- Attack (deal damage based on your Strength + position bonus)
- Defend (reduce incoming damage by your Defense)
- Insight (learn about opponent's hidden attributes)

MOVEMENT:
- Advance (move closer, gain Momentum, lose Balance)
- Retreat{"" if turn <= 3 else " (FORBIDDEN after turn 3 - honor violation!)"}

COMBINATION PLAYS:
- Advance + Attack (aggressive rush)
- Advance + Defend (cautious advance)
- Retreat + Attack (hit and run){"" if turn <= 3 else " (ONLY if turn <= 3)"}
- Retreat + Defend (full defense){"" if turn <= 3 else " (ONLY if turn <= 3)"}

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

# ==================== PLAYER AGENT ====================

class BushidoPlayerAgent:
    """
    Human-like player agent using reasoning chains
    Based on Chapter 17: Reasoning Techniques (page 241-261)
    """

    def __init__(self, state: PlayerState, game_state: GameState):
        self.state = state
        self.game_state = game_state
        self.session_id = f"game_{game_state.game_id}_{state.role.value}"
        self.user_id = f"player_{state.persona.name}"
        self.agent = self._create_agent()
        self.runner = InMemoryRunner(self.agent, app_name="BushidoGame")

        # Initialize session in the runner's session service
        try:
            if hasattr(self.runner, 'session_service') and hasattr(self.runner.session_service, 'create_session'):
                self.runner.session_service.create_session(session_id=self.session_id)
                logger.debug(f"Initialized session: {self.session_id}")
        except Exception as e:
            logger.debug(f"Session initialization note: {e} (may auto-create on first use)")

    def _create_agent(self) -> Agent:
        """Create ADK agent with human-like reasoning"""

        # Personality-specific instructions
        persona_instructions = self._generate_persona_instructions()

        # Create tools with access to game state
        tools = create_player_tools(self.state, self.game_state)

        return Agent(
            name=f"Player_{self.state.persona.name}",
            model="gemini-2.0-flash-exp",
            description=f"A {self.state.persona.personality.value} player in a tactical card duel",
            instruction=f"""
You are playing a tactical samurai card duel game as {self.state.persona.name}.
Your personality: {self.state.persona.personality.value}
Risk tolerance: {self.state.persona.risk_tolerance:.2f}

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
""",
            tools=tools
        )
    
    def _generate_persona_instructions(self) -> str:
        """Generate personality-specific playing instructions"""
        
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
        
        return instructions.get(self.state.persona.personality, "")

    async def get_decision_from_agent(self) -> Dict[str, Any]:
        """
        Invoke the agent via runner to get a decision
        Returns parsed decision with actions, technique, and reasoning
        """
        try:
            # Create the prompt for this turn
            prompt = f"""
It's your turn in the duel! You are {self.state.persona.name}.

Current game state:
- Turn: {self.game_state.turn_number}
- Your health: {self.state.health}/3
- Opponent health: {(self.game_state.defender if self.state.role == PlayerRole.CHALLENGER else self.game_state.challenger).health}/3

Use your tools to analyze the situation and make your decision.
Think through your options carefully, express your thoughts, and then provide your decision.
"""

            # Create message
            message = types.Content(
                parts=[types.Part(text=prompt)]
            )

            # Run the agent
            full_response = ""
            try:
                async for event in self.runner.run_async(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    new_message=message
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                full_response += part.text
            except Exception as session_error:
                # If session error, try without session_id (let runner auto-create)
                logger.warning(f"Session error, retrying without explicit session_id: {session_error}")
                async for event in self.runner.run_async(
                    user_id=self.user_id,
                    session_id=f"{self.session_id}_retry_{self.game_state.turn_number}",
                    new_message=message
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                full_response += part.text

            logger.info(f"{self.state.persona.name} reasoning:\n{full_response[:200]}...")

            # Parse the decision from response
            decision = self._parse_decision(full_response)

            # Update emotional state based on game situation
            opponent = (self.game_state.defender if self.state.role == PlayerRole.CHALLENGER
                       else self.game_state.challenger)
            observations = {
                "tension_level": decision["tension"],
                "opponent_health": opponent.health
            }
            self._update_emotional_state(observations)

            return decision

        except Exception as e:
            logger.error(f"Error getting decision from agent: {e}")
            logger.info("Falling back to deterministic decision making")
            return self._fallback_decision()

    def _parse_decision(self, response: str) -> Dict[str, Any]:
        """Parse agent's response to extract decision"""
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

        # Calculate metrics for this decision
        tension = self._calculate_tension()
        enjoyment = self._calculate_enjoyment(actions_tuple)
        choice_difficulty = 0.5  # Could be enhanced with more analysis

        return {
            "actions": actions_tuple,
            "technique": technique,
            "reasoning": reasoning,
            "deliberation": response[:200],  # First 200 chars of full reasoning
            "tension": tension,
            "enjoyment": enjoyment,
            "choice_difficulty": choice_difficulty
        }

    def _fallback_decision(self) -> Dict[str, Any]:
        """Fallback to deterministic decision if LLM fails"""
        # Use the existing logic as fallback
        situation = self.analyze_situation()
        options = self.evaluate_options(situation)
        return self.make_decision(options)

    def _calculate_tension(self) -> float:
        """Calculate current tension level"""
        health_pressure = 1.0 - (self.state.health / 3.0)
        turn_pressure = min(self.game_state.turn_number / 5.0, 1.0)
        return (health_pressure + turn_pressure) / 2

    def _calculate_enjoyment(self, actions: Tuple[ActionCard, ...]) -> float:
        """Calculate expected enjoyment from action"""
        enjoyment = 0.5

        if self.state.persona.personality == PersonalityTrait.AGGRESSIVE:
            if ActionCard.ATTACK in actions:
                enjoyment += 0.3
        elif self.state.persona.personality == PersonalityTrait.DEFENSIVE:
            if ActionCard.DEFEND in actions:
                enjoyment += 0.3

        return min(enjoyment, 1.0)

    def analyze_situation(self) -> Dict[str, Any]:
        """
        Analyze current game situation with human-like observations
        Pattern: Reasoning-Based Information Extraction (page 152)
        """
        
        # Calculate tension based on game state
        health_pressure = 1.0 - (self.state.health / 3.0)
        turn_pressure = min(self.game_state.turn_number / 5.0, 1.0)
        
        opponent = (self.game_state.defender 
                   if self.state.role == PlayerRole.CHALLENGER 
                   else self.game_state.challenger)
        
        # Human-like observations
        observations = {
            "my_health": self.state.health,
            "opponent_health": opponent.health,
            "position": self.game_state.position.value,
            "my_resources": {
                "momentum": self.state.momentum,
                "balance": self.state.balance
            },
            "opponent_resources": {
                "momentum": opponent.momentum,
                "balance": opponent.balance
            },
            "turn": self.game_state.turn_number,
            "tension_level": (health_pressure + turn_pressure) / 2,
            "emotional_reading": self._read_opponent_emotion(opponent),
            "pattern_recognition": self._recognize_patterns()
        }
        
        # Update emotional state based on situation
        self._update_emotional_state(observations)
        
        return observations
    
    def _read_opponent_emotion(self, opponent: PlayerState) -> str:
        """Attempt to read opponent's emotional state"""
        if opponent.momentum >= 2:
            return "aggressive_confident"
        elif opponent.balance >= 2:
            return "defensive_cautious"
        elif opponent.health == 1:
            return "desperate_dangerous"
        else:
            return "neutral_unreadable"
    
    def _recognize_patterns(self) -> Dict[str, Any]:
        """Recognize patterns from game history"""
        if len(self.game_state.turn_history) < 2:
            return {"identified": False, "pattern": None}
        
        # Simple pattern recognition
        last_turns = self.game_state.turn_history[-2:]
        
        # Check for repeated actions
        if all(turn.get("opponent_action") == ActionCard.ADVANCE.value 
               for turn in last_turns):
            return {"identified": True, "pattern": "aggressive_rush"}
        elif all(turn.get("opponent_action") == ActionCard.DEFEND.value 
                for turn in last_turns):
            return {"identified": True, "pattern": "turtle_defense"}
        
        return {"identified": False, "pattern": None}
    
    def _update_emotional_state(self, observations: Dict):
        """Update emotional state based on game situation"""
        tension = observations["tension_level"]
        
        if self.state.health == 1:
            self.state.persona.emotional_state = "desperate"
            self.state.persona.confidence_level *= 0.7
        elif tension > self.state.persona.tension_threshold:
            self.state.persona.emotional_state = "tense"
            self.state.persona.confidence_level *= 0.9
        elif observations["opponent_health"] == 1:
            self.state.persona.emotional_state = "excited"
            self.state.persona.confidence_level *= 1.2
        else:
            self.state.persona.emotional_state = "focused"
        
        # Clamp confidence
        self.state.persona.confidence_level = max(0.1, min(1.0, 
                                                  self.state.persona.confidence_level))
    
    def evaluate_options(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate available options with human-like reasoning
        Pattern: Tree of Thoughts (page 245)
        """
        
        options = []
        position = Position[self.game_state.position.name]
        
        # Generate possible moves based on position
        possible_actions = self._get_possible_actions(position)
        
        for action_combo in possible_actions:
            option = {
                "actions": action_combo,
                "reasoning": self._reason_about_option(action_combo, situation),
                "emotional_response": self._emotional_response_to_option(action_combo),
                "perceived_risk": self._calculate_risk(action_combo, situation),
                "expected_enjoyment": self._calculate_enjoyment(action_combo)
            }
            
            # Score based on personality
            option["score"] = self._score_option(option)
            options.append(option)
        
        return sorted(options, key=lambda x: x["score"], reverse=True)
    
    def _get_possible_actions(self, position: Position) -> List[Tuple[ActionCard, ...]]:
        """Get valid action combinations for current position"""
        
        possible = []
        
        # Stay put
        possible.append(())
        possible.append((ActionCard.ATTACK,))
        possible.append((ActionCard.DEFEND,))
        possible.append((ActionCard.INSIGHT,))
        
        # Advance
        possible.append((ActionCard.ADVANCE,))
        possible.append((ActionCard.ADVANCE,ActionCard.ATTACK))
        possible.append((ActionCard.ADVANCE,ActionCard.DEFEND))
        possible.append((ActionCard.ADVANCE,ActionCard.INSIGHT))
        
        # Retreat
        if self.game_state.turn_number <= 3:
            possible.append((ActionCard.RETREAT,))
            possible.append((ActionCard.RETREAT,ActionCard.ATTACK))
            possible.append((ActionCard.RETREAT,ActionCard.DEFEND))
            possible.append((ActionCard.RETREAT,ActionCard.INSIGHT))
        
        return possible
    
    def _reason_about_option(self, actions: Tuple[ActionCard, ...], 
                            situation: Dict) -> str:
        """Generate human-like reasoning for an option"""
        
        if not actions:
            return "Stay put and build balance. Safe but passive."
        
        reasoning = []
        for action in actions:
            if action == ActionCard.ATTACK:
                reasoning.append(f"Attack while they have {situation['opponent_health']} health")
            elif action == ActionCard.DEFEND:
                reasoning.append("Defend to minimize damage")
            elif action == ActionCard.ADVANCE:
                reasoning.append("Close the distance")
            elif action == ActionCard.RETREAT:
                reasoning.append("Create space for safety")
            elif action == ActionCard.INSIGHT:
                reasoning.append("Learn about opponent's capabilities")
        
        return ". ".join(reasoning)
    
    def _emotional_response_to_option(self, actions: Tuple[ActionCard, ...]) -> str:
        """Generate emotional response to option"""
        
        personality = self.state.persona.personality
        
        responses = {
            PersonalityTrait.AGGRESSIVE: {
                ActionCard.ATTACK: "Yes! Time to strike!",
                ActionCard.DEFEND: "Ugh, playing it safe...",
                ActionCard.ADVANCE: "Push forward!",
                ActionCard.RETREAT: "This feels wrong..."
            },
            PersonalityTrait.DEFENSIVE: {
                ActionCard.ATTACK: "Risky, but might be necessary",
                ActionCard.DEFEND: "Good, protect myself",
                ActionCard.ADVANCE: "Nervous about getting closer",
                ActionCard.RETREAT: "Smart move, stay safe"
            },
            PersonalityTrait.UNPREDICTABLE: {
                ActionCard.ATTACK: "They won't expect this!",
                ActionCard.DEFEND: "Let's confuse them",
                ActionCard.ADVANCE: "Chaos time!",
                ActionCard.RETREAT: "Strategic misdirection"
            }
        }
        
        if not actions:
            return "Patience... patience..."
        
        response = responses.get(personality, {})
        return response.get(actions[0], "Interesting choice...")
    
    def _calculate_risk(self, actions: Tuple[ActionCard, ...], 
                       situation: Dict) -> float:
        """Calculate perceived risk of action"""
        
        risk = 0.0
        
        if ActionCard.ATTACK in actions:
            # Risk of being countered
            risk += 0.4
            if situation["opponent_resources"]["balance"] >= 2:
                risk += 0.3
        
        if ActionCard.ADVANCE in actions:
            # Risk of getting too close
            risk += 0.2
            if self.state.health == 1:
                risk += 0.4
        
        if ActionCard.INSIGHT in actions:
            # Risk of being attacked while learning
            risk += 0.6 if situation["position"] != "Apart" else 0.1
        
        return min(risk, 1.0)
    
    def _calculate_enjoyment(self, actions: Tuple[ActionCard, ...]) -> float:
        """Calculate expected enjoyment from action"""
        
        enjoyment = 0.5  # Base enjoyment
        
        # Personality-based enjoyment
        if self.state.persona.personality == PersonalityTrait.AGGRESSIVE:
            if ActionCard.ATTACK in actions:
                enjoyment += 0.3
            if ActionCard.ADVANCE in actions:
                enjoyment += 0.2
        elif self.state.persona.personality == PersonalityTrait.DEFENSIVE:
            if ActionCard.DEFEND in actions:
                enjoyment += 0.3
        elif self.state.persona.personality == PersonalityTrait.UNPREDICTABLE:
            # Enjoys variety
            if len(self.state.strategy_log) > 0:
                last_action = self.state.strategy_log[-1].get("actions")
                if last_action != actions:
                    enjoyment += 0.4
        
        return min(enjoyment, 1.0)
    
    def _score_option(self, option: Dict) -> float:
        """Score option based on personality and situation"""
        
        # Base score from risk/reward
        score = 1.0 - option["perceived_risk"] * (1.0 - self.state.persona.risk_tolerance)
        
        # Add enjoyment factor
        score += option["expected_enjoyment"] * 0.3
        
        # Personality modifiers
        if self.state.persona.personality == PersonalityTrait.CALCULATED:
            # Focus on optimal play
            score *= 1.0 if option["perceived_risk"] < 0.3 else 0.7
        elif self.state.persona.personality == PersonalityTrait.HONORABLE:
            # Avoid retreat after turn 3
            if ActionCard.RETREAT in option["actions"] and self.game_state.turn_number > 3:
                score *= 0.1
        
        # Confidence modifier
        score *= (0.5 + self.state.persona.confidence_level * 0.5)
        
        return score
    
    def make_decision(self, options: List[Dict]) -> Dict[str, Any]:
        """
        Make final decision with human-like deliberation
        Pattern: Self-consistency (page 342)
        """

        # Pick top option but with some personality-based variation
        if self.state.persona.personality == PersonalityTrait.UNPREDICTABLE:
            # Sometimes pick suboptimal for surprise
            if random.random() < 0.3 and len(options) > 1:
                chosen = options[1]  # Pick second best
                deliberation = "Let's keep them guessing..."
            else:
                chosen = options[0]
                deliberation = "This seems right, but who knows?"
        else:
            chosen = options[0]
            deliberation = self._generate_deliberation(chosen, options)
        
        # Record decision in strategy log
        self.state.strategy_log.append({
            "turn": self.game_state.turn_number,
            "actions": chosen["actions"],
            "reasoning": chosen["reasoning"],
            "emotion": self.state.persona.emotional_state,
            "confidence": self.state.persona.confidence_level
        })
        
        # Calculate tension and enjoyment for this decision
        tension = chosen["perceived_risk"] * 0.5 + (1.0 - self.state.health / 3.0) * 0.5
        enjoyment = chosen["expected_enjoyment"]
        
        # Check for hard choice (multiple good options)
        choice_difficulty = 0.0
        if len(options) > 1:
            score_difference = options[0]["score"] - options[1]["score"]
            if score_difference < 0.1:
                choice_difficulty = 0.8
                deliberation += " This was a really tough choice!"
        
        return {
            "actions": chosen["actions"],
            "technique": self._select_technique(chosen["actions"]),
            "reasoning": chosen["reasoning"],
            "deliberation": deliberation,
            "tension": tension,
            "enjoyment": enjoyment,
            "choice_difficulty": choice_difficulty
        }
    
    def _generate_deliberation(self, chosen: Dict, options: List[Dict]) -> str:
        """Generate human-like deliberation text"""
        
        if self.state.persona.emotional_state == "desperate":
            return "No choice... I have to do this or I'm done!"
        elif self.state.persona.emotional_state == "excited":
            return "This is it! Time to finish this!"
        elif len(options) > 1 and options[0]["score"] - options[1]["score"] < 0.2:
            return "Tough call, but I think this is the right move..."
        else:
            return f"Given the situation, {chosen['emotional_response']}"
    
    def _select_technique(self, actions: Tuple[ActionCard, ...]) -> str:
        """Select appropriate technique card for the action"""
        
        if not self.state.technique_cards:
            return None
        
        # Simple technique selection based on action
        if ActionCard.ATTACK in actions:
            if self.state.momentum >= 2:
                return "Tsubame Gaeshi"
            else:
                return self.state.technique_cards[0]
        elif ActionCard.DEFEND in actions:
            if self.state.balance >= 2:
                return "Mizu no Kokoro"
            else:
                return self.state.technique_cards[0]
        
        return self.state.technique_cards[0]

# ==================== GAME MASTER AGENT ====================

class GameMasterAgent:
    """
    Root agent that manages game flow and rules
    Pattern: Orchestrator (implied throughout book's multi-agent examples)
    """
    
    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.game_state = None
        self.player_agents = {}
        self.logger = logging.getLogger(f"GameMaster_{simulation_id}")
        
    async def initialize_game(self, personas: Tuple[PlayerPersona, PlayerPersona]) -> GameState:
        """Initialize a new game with given personas"""
        
        self.game_state = GameState(
            game_id=str(uuid.uuid4()),
            position=Position.APART
        )
        
        # Initialize challenger
        self.game_state.challenger = PlayerState(
            role=PlayerRole.CHALLENGER,
            persona=personas[0],
            momentum=1,  # Challenger starts with momentum
            balance=0
        )
        
        # Initialize defender
        self.game_state.defender = PlayerState(
            role=PlayerRole.DEFENDER,
            persona=personas[1],
            momentum=0,
            balance=1  # Defender starts with balance
        )
        
        # Assign technique cards
        self._assign_techniques()
        
        # Create player agents
        self.player_agents[PlayerRole.CHALLENGER] = BushidoPlayerAgent(
            self.game_state.challenger, self.game_state
        )
        self.player_agents[PlayerRole.DEFENDER] = BushidoPlayerAgent(
            self.game_state.defender, self.game_state
        )
        
        self.logger.info(f"Game {self.game_state.game_id} initialized")
        return self.game_state
    
    def _assign_techniques(self):
        """Assign technique cards to players"""
        available_techniques = list(TECHNIQUE_CARDS.keys())
        random.shuffle(available_techniques)
        
        # Remove one random card
        available_techniques.pop()
        
        # Draft process as per rules
        self.game_state.challenger.technique_cards = [
            available_techniques[0],
            available_techniques[2]
        ]
        self.game_state.defender.technique_cards = [
            available_techniques[1],
            available_techniques[3]
        ]
    
    async def run_turn(self) -> Dict[str, Any]:
        """Execute a single game turn"""
        
        self.game_state.turn_number += 1
        self.logger.info(f"Starting turn {self.game_state.turn_number}")
        
        # Get decisions from both players in parallel
        # Pattern: Parallelization (Chapter 3, page 32)
        challenger_task = asyncio.create_task(
            self._get_player_decision(PlayerRole.CHALLENGER)
        )
        defender_task = asyncio.create_task(
            self._get_player_decision(PlayerRole.DEFENDER)
        )
        
        challenger_decision, defender_decision = await asyncio.gather(
            challenger_task, defender_task
        )
        
        # Resolve turn
        turn_result = self._resolve_turn(challenger_decision, defender_decision)
        
        # Update game state
        self._update_game_state(turn_result)
        
        # Log turn
        self.game_state.turn_history.append(turn_result)
        
        # Record psychological metrics
        self.game_state.tension_levels.append(
            (challenger_decision["tension"] + defender_decision["tension"]) / 2
        )
        self.game_state.choice_difficulty.append(
            (challenger_decision["choice_difficulty"] + 
             defender_decision["choice_difficulty"]) / 2
        )
        self.game_state.enjoyment_scores.append(
            (challenger_decision["enjoyment"] + defender_decision["enjoyment"]) / 2
        )
        
        return turn_result
    
    async def _get_player_decision(self, role: PlayerRole) -> Dict[str, Any]:
        """Get decision from player agent using LLM reasoning"""

        agent = self.player_agents[role]

        # Get decision from agent via LLM invocation
        decision = await agent.get_decision_from_agent()

        self.logger.info(f"{role.value} decision: {decision['actions']}")
        self.logger.info(f"  Reasoning: {decision['reasoning']}")
        self.logger.info(f"  Emotion: {agent.state.persona.emotional_state}")

        return decision
    
    def _resolve_turn(self, challenger_decision: Dict, 
                     defender_decision: Dict) -> Dict[str, Any]:
        """Resolve turn according to game rules"""
        
        result = {
            "turn": self.game_state.turn_number,
            "challenger_actions": challenger_decision["actions"],
            "defender_actions": defender_decision["actions"],
            "challenger_technique": challenger_decision["technique"],
            "defender_technique": defender_decision["technique"],
            "position_before": self.game_state.position.value,
            "damage_dealt": {"challenger": 0, "defender": 0}
        }
        
        # Resolve position changes
        new_position = self._resolve_position(
            challenger_decision["actions"],
            defender_decision["actions"]
        )
        result["position_after"] = new_position.value
        self.game_state.position = new_position
        
        # Resolve combat if applicable
        if new_position != Position.APART:
            damage = self._resolve_combat(
                challenger_decision,
                defender_decision,
                new_position
            )
            result["damage_dealt"] = damage
        
        # Check for honor violation
        if self.game_state.turn_number > 3:
            if ActionCard.RETREAT in challenger_decision["actions"]:
                result["honor_violation"] = "Challenger"
            if ActionCard.RETREAT in defender_decision["actions"]:
                result["honor_violation"] = "Defender"
        
        return result
    
    def _resolve_position(self, challenger_actions: Tuple[ActionCard, ...],
                         defender_actions: Tuple[ActionCard, ...]) -> Position:
        """Resolve position changes based on movements"""
        
        current = self.game_state.position
        
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
        if current == Position.APART:
            if challenger_move == ActionCard.ADVANCE or defender_move == ActionCard.ADVANCE:
                if challenger_move != ActionCard.RETREAT and defender_move != ActionCard.RETREAT:
                    return Position.SWORD
        elif current == Position.SWORD:
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
        elif current == Position.CLOSE:
            if challenger_move == ActionCard.RETREAT and defender_move == ActionCard.RETREAT:
                return Position.APART
            elif challenger_move == ActionCard.RETREAT and defender_move != ActionCard.ADVANCE:
                return Position.SWORD
            elif defender_move == ActionCard.RETREAT and challenger_move != ActionCard.ADVANCE:
                return Position.SWORD
        
        return current
    
    def _resolve_combat(self, challenger_decision: Dict,
                       defender_decision: Dict,
                       position: Position) -> Dict[str, int]:
        """Resolve combat exchanges"""
        
        damage = {"challenger": 0, "defender": 0}
        
        # Check for attacks
        challenger_attacking = ActionCard.ATTACK in challenger_decision["actions"]
        defender_attacking = ActionCard.ATTACK in defender_decision["actions"]
        
        if not (challenger_attacking or defender_attacking):
            return damage
        
        # Calculate attack and defense totals
        if challenger_attacking:
            attack_total = self.game_state.challenger.strength
            if ActionCard.ADVANCE in challenger_decision["actions"]:
                attack_total += 1
            if position == Position.CLOSE:
                attack_total += 1
            
            defense_total = 0
            if ActionCard.DEFEND in defender_decision["actions"]:
                defense_total = self.game_state.defender.defense
                if ActionCard.RETREAT in defender_decision["actions"]:
                    defense_total += 1
            
            damage["defender"] = max(0, attack_total - defense_total)
        
        if defender_attacking:
            attack_total = self.game_state.defender.strength
            if ActionCard.ADVANCE in defender_decision["actions"]:
                attack_total += 1
            if position == Position.CLOSE:
                attack_total += 1
            
            defense_total = 0
            if ActionCard.DEFEND in challenger_decision["actions"]:
                defense_total = self.game_state.challenger.defense
                if ActionCard.RETREAT in challenger_decision["actions"]:
                    defense_total += 1
            
            damage["challenger"] = max(0, attack_total - defense_total)
        
        return damage
    
    def _update_game_state(self, turn_result: Dict):
        """Update game state after turn resolution"""
        
        # Apply damage
        self.game_state.challenger.health -= turn_result["damage_dealt"]["challenger"]
        self.game_state.defender.health -= turn_result["damage_dealt"]["defender"]
        
        # Update resources based on actions
        for action in turn_result["challenger_actions"]:
            if action == ActionCard.ADVANCE:
                self.game_state.challenger.momentum = min(3, 
                    self.game_state.challenger.momentum + 1)
                self.game_state.challenger.balance = max(0,
                    self.game_state.challenger.balance - 1)
            elif action == ActionCard.RETREAT:
                self.game_state.challenger.momentum = max(0,
                    self.game_state.challenger.momentum - 1)
        
        if not turn_result["challenger_actions"]:
            self.game_state.challenger.balance = min(3,
                self.game_state.challenger.balance + 1)
        
        # Same for defender
        for action in turn_result["defender_actions"]:
            if action == ActionCard.ADVANCE:
                self.game_state.defender.momentum = min(3,
                    self.game_state.defender.momentum + 1)
                self.game_state.defender.balance = max(0,
                    self.game_state.defender.balance - 1)
            elif action == ActionCard.RETREAT:
                self.game_state.defender.momentum = max(0,
                    self.game_state.defender.momentum - 1)
        
        if not turn_result["defender_actions"]:
            self.game_state.defender.balance = min(3,
                self.game_state.defender.balance + 1)
    
    def check_victory(self) -> Optional[str]:
        """Check for victory conditions"""
        
        if self.game_state.challenger.health <= 0 and self.game_state.defender.health <= 0:
            return "DRAW"
        elif self.game_state.challenger.health <= 0:
            return "DEFENDER"
        elif self.game_state.defender.health <= 0:
            return "CHALLENGER"
        
        # Check for honor violation
        if self.game_state.turn_history:
            last_turn = self.game_state.turn_history[-1]
            if "honor_violation" in last_turn:
                if last_turn["honor_violation"] == "Challenger":
                    return "DEFENDER"
                elif last_turn["honor_violation"] == "Defender":
                    return "CHALLENGER"
        
        return None
    
    async def complete_game(self) -> Dict[str, Any]:
        """Complete the game and generate summary"""

        winner = self.check_victory()

        summary = {
            "game_id": self.game_state.game_id,
            "winner": winner,
            "total_turns": self.game_state.turn_number,
            "final_health": {
                "challenger": self.game_state.challenger.health,
                "defender": self.game_state.defender.health
            },
            "average_tension": sum(self.game_state.tension_levels) / len(self.game_state.tension_levels) if self.game_state.tension_levels else 0,
            "average_choice_difficulty": sum(self.game_state.choice_difficulty) / len(self.game_state.choice_difficulty) if self.game_state.choice_difficulty else 0,
            "average_enjoyment": sum(self.game_state.enjoyment_scores) / len(self.game_state.enjoyment_scores) if self.game_state.enjoyment_scores else 0,
            "turn_history": self.game_state.turn_history
        }

        # Cleanup agent runners
        await self.cleanup()

        return summary

    async def cleanup(self):
        """Cleanup agent runners to free resources"""
        try:
            for agent in self.player_agents.values():
                if hasattr(agent, 'runner') and agent.runner:
                    await agent.runner.close()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

# ==================== SIMULATION ORCHESTRATOR ====================

class SimulationOrchestrator:
    """
    Main orchestrator for running multiple game simulations
    Pattern: Parallelization (Chapter 3, page 32)
    """
    
    def __init__(self):
        self.simulations = []
        self.results = []
        
    async def run_simulations(self, num_simulations: int) -> List[Dict[str, Any]]:
        """Run multiple game simulations in parallel"""
        
        logger.info(f"Starting {num_simulations} simulations")
        
        # Create diverse persona pairs
        persona_pairs = self._generate_persona_pairs(num_simulations)
        
        # Run simulations in parallel (batched for resource management)
        # Pattern: Resource-Aware Optimization (Chapter 16, page 225)
        batch_size = 5  # Run 5 games at a time
        
        for i in range(0, num_simulations, batch_size):
            batch_end = min(i + batch_size, num_simulations)
            batch_tasks = []
            
            for j in range(i, batch_end):
                task = asyncio.create_task(
                    self._run_single_simulation(j, persona_pairs[j])
                )
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            self.results.extend(batch_results)
            
            logger.info(f"Completed {batch_end}/{num_simulations} simulations")
        
        return self.results
    
    def _generate_persona_pairs(self, count: int) -> List[Tuple[PlayerPersona, PlayerPersona]]:
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
                learning_rate=random.uniform(0.1, 0.5),
                tension_threshold=random.uniform(0.5, 0.9),
                enjoyment_factors=["close_matches", "successful_reads", "dramatic_moments"]
            )
            
            p2 = PlayerPersona(
                name=f"Player_{i}_B",
                personality=p2_personality,
                risk_tolerance=random.uniform(0.2, 0.9),
                learning_rate=random.uniform(0.1, 0.5),
                tension_threshold=random.uniform(0.5, 0.9),
                enjoyment_factors=["outsmarting_opponent", "perfect_defense", "comeback_victories"]
            )
            
            pairs.append((p1, p2))
        
        return pairs
    
    async def _run_single_simulation(self, sim_id: int, 
                                    personas: Tuple[PlayerPersona, PlayerPersona]) -> Dict[str, Any]:
        """Run a single game simulation"""
        
        logger.info(f"Simulation {sim_id}: {personas[0].name} vs {personas[1].name}")
        
        gm = GameMasterAgent(f"sim_{sim_id}")
        await gm.initialize_game(personas)
        
        # Run game until completion
        max_turns = 10  # Safety limit
        
        for turn in range(max_turns):
            turn_result = await gm.run_turn()
            
            winner = gm.check_victory()
            if winner:
                logger.info(f"Simulation {sim_id} completed: {winner} wins!")
                break
        
        # Get game summary
        summary = await gm.complete_game()
        summary["simulation_id"] = sim_id
        summary["personas"] = {
            "challenger": personas[0].personality.value,
            "defender": personas[1].personality.value
        }
        
        return summary
    
    async def generate_evaluation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report
        Pattern: Self-refinement (Chapter 8, page 246)
        """
        
        if not self.results:
            return {"error": "No simulation results available"}
        
        # Analyze game balance
        balance_metrics = self._analyze_balance()
        
        # Analyze engagement metrics
        engagement_metrics = self._analyze_engagement()
        
        # Analyze personality matchups
        matchup_analysis = self._analyze_matchups()
        
        report = {
            "total_simulations": len(self.results),
            "balance_metrics": balance_metrics,
            "engagement_metrics": engagement_metrics,
            "matchup_analysis": matchup_analysis,
            "recommendations": self._generate_recommendations(
                balance_metrics, engagement_metrics
            ),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _analyze_balance(self) -> Dict[str, Any]:
        """Analyze game balance from results"""
        
        challenger_wins = sum(1 for r in self.results if r["winner"] == "CHALLENGER")
        defender_wins = sum(1 for r in self.results if r["winner"] == "DEFENDER")
        draws = sum(1 for r in self.results if r["winner"] == "DRAW")
        
        return {
            "challenger_win_rate": challenger_wins / len(self.results),
            "defender_win_rate": defender_wins / len(self.results),
            "draw_rate": draws / len(self.results),
            "average_game_length": sum(r["total_turns"] for r in self.results) / len(self.results),
            "health_differential": sum(abs(r["final_health"]["challenger"] - 
                                         r["final_health"]["defender"]) 
                                      for r in self.results) / len(self.results)
        }
    
    def _analyze_engagement(self) -> Dict[str, Any]:
        """Analyze player engagement metrics"""
        
        return {
            "average_tension": sum(r["average_tension"] for r in self.results) / len(self.results),
            "average_choice_difficulty": sum(r["average_choice_difficulty"] 
                                           for r in self.results) / len(self.results),
            "average_enjoyment": sum(r["average_enjoyment"] for r in self.results) / len(self.results),
            "high_tension_games": sum(1 for r in self.results if r["average_tension"] > 0.7) / len(self.results),
            "high_enjoyment_games": sum(1 for r in self.results if r["average_enjoyment"] > 0.7) / len(self.results)
        }
    
    def _analyze_matchups(self) -> Dict[str, Dict[str, float]]:
        """Analyze personality matchup results"""
        
        matchup_data = {}
        
        for result in self.results:
            matchup_key = f"{result['personas']['challenger']}_vs_{result['personas']['defender']}"
            
            if matchup_key not in matchup_data:
                matchup_data[matchup_key] = {
                    "games": 0,
                    "challenger_wins": 0,
                    "total_enjoyment": 0,
                    "total_tension": 0
                }
            
            matchup_data[matchup_key]["games"] += 1
            if result["winner"] == "CHALLENGER":
                matchup_data[matchup_key]["challenger_wins"] += 1
            matchup_data[matchup_key]["total_enjoyment"] += result["average_enjoyment"]
            matchup_data[matchup_key]["total_tension"] += result["average_tension"]
        
        # Calculate averages
        for matchup in matchup_data.values():
            if matchup["games"] > 0:
                matchup["win_rate"] = matchup["challenger_wins"] / matchup["games"]
                matchup["avg_enjoyment"] = matchup["total_enjoyment"] / matchup["games"]
                matchup["avg_tension"] = matchup["total_tension"] / matchup["games"]
        
        return matchup_data
    
    def _generate_recommendations(self, balance: Dict, engagement: Dict) -> List[str]:
        """Generate recommendations for game improvement"""
        
        recommendations = []
        
        # Balance recommendations
        if abs(balance["challenger_win_rate"] - 0.5) > 0.15:
            if balance["challenger_win_rate"] > 0.5:
                recommendations.append("Consider buffing Defender's starting resources")
            else:
                recommendations.append("Consider buffing Challenger's starting momentum")
        
        # Engagement recommendations
        if engagement["average_tension"] < 0.5:
            recommendations.append("Games may be too predictable - consider adding more swing mechanics")
        
        if engagement["average_enjoyment"] < 0.6:
            recommendations.append("Player enjoyment is low - consider adding more meaningful choices")
        
        if engagement["average_choice_difficulty"] < 0.3:
            recommendations.append("Choices may be too obvious - consider balancing option values")
        
        if balance["average_game_length"] < 3:
            recommendations.append("Games ending too quickly - consider increasing starting health")
        elif balance["average_game_length"] > 7:
            recommendations.append("Games may be dragging - consider increasing damage potential")
        
        return recommendations if recommendations else ["Game appears well-balanced!"]

# ==================== MAIN EXECUTION ====================

async def main():
    """Main execution function"""

    # Initialize Vertex AI
    vertex_initialized = initialize_vertex_ai()
    if not vertex_initialized:
        print("\nWARNING: Running without Vertex AI. Set GOOGLE_CLOUD_PROJECT environment variable for LLM-powered agents.")
        print("The system will fall back to deterministic decision-making.\n")

    print("=" * 60)
    print("BUSHIDO CARD GAME - AUTOMATED PLAYTESTING SYSTEM")
    print("Using human-like reasoning agents" if vertex_initialized else "Using deterministic AI")
    print("=" * 60)
    
    # Get number of simulations from user
    try:
        num_sims = int(input("\nHow many game simulations would you like to run? "))
        if num_sims <= 0:
            print("Number must be positive. Using default: 5")
            num_sims = 5
    except ValueError:
        print("Invalid input. Using default: 5 simulations")
        num_sims = 5

    print(f"\nRunning {num_sims} simulations with diverse player personalities...")
    print("This will generate human-like gameplay with emotional responses.\n")
    
    # Create orchestrator
    orchestrator = SimulationOrchestrator()
    
    # Run simulations
    results = await orchestrator.run_simulations(num_sims)
    
    # Generate evaluation report
    print("\nGenerating evaluation report...")
    report = await orchestrator.generate_evaluation_report()
    
    # Save results
    try:
        output_dir = Path("./simulation_results")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        with open(output_dir / f"results_{timestamp}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save evaluation report
        with open(output_dir / f"evaluation_{timestamp}.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nResults saved to {output_dir}")
        print(f"  - Detailed results: results_{timestamp}.json")
        print(f"  - Evaluation report: evaluation_{timestamp}.json")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        print(f"\nWARNING: Could not save results to file: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print(f"\nBalance Metrics:")
    print(f"  Challenger Win Rate: {report['balance_metrics']['challenger_win_rate']:.1%}")
    print(f"  Defender Win Rate: {report['balance_metrics']['defender_win_rate']:.1%}")
    print(f"  Average Game Length: {report['balance_metrics']['average_game_length']:.1f} turns")
    
    print(f"\nEngagement Metrics:")
    print(f"  Average Tension: {report['engagement_metrics']['average_tension']:.2f}")
    print(f"  Average Enjoyment: {report['engagement_metrics']['average_enjoyment']:.2f}")
    print(f"  High Tension Games: {report['engagement_metrics']['high_tension_games']:.1%}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")

if __name__ == "__main__":
    asyncio.run(main())
