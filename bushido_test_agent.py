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
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types
import vertexai

# Import from refactored modules
from models import (
    Position, ActionCard, PlayerRole, PersonalityTrait,
    PlayerPersona, PlayerState, GameState
)
from constants import TECHNIQUE_CARDS, MAX_TURNS, HONOR_RESTRICTION_TURN
from resource_manager import PlayerResourceManager
from rules_engine import GameRulesEngine
from metrics_tracker import MetricsTracker


# ==================== LOGGING CONFIGURATION ====================

# Configure logging to file with INFO level (only INFO, WARNING, ERROR)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bushido_simulation.log',
    filemode='w'  # Overwrite log file each run for cleaner debugging
)
logger = logging.getLogger(__name__)

# Suppress verbose logs from google_adk and google.auth
logging.getLogger('google_adk').setLevel(logging.WARNING)
logging.getLogger('google.auth').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)


# ==================== ENVIRONMENT CONFIGURATION ====================

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


# ==================== INITIALIZATION ====================

def initialize_vertex_ai() -> bool:
    """Initialize Vertex AI with error handling"""
    if not PROJECT_ID:
        logger.warning("GOOGLE_CLOUD_PROJECT not set. Set environment variable for production use.")
        logger.warning("Running in test mode without Vertex AI.")
        return False

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        logger.info(f"Vertex AI initialized: project={PROJECT_ID}, location={LOCATION}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        logger.warning("Running in test mode without Vertex AI.")
        return False


# ==================== TOOL FUNCTIONS ====================

def create_player_tools(player_state: PlayerState, game_state: GameState) -> List[FunctionTool]:
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

        logger.info(f"[INIT] Creating agent for {state.persona.name} ({state.role.value})")
        logger.info(f"[INIT] Session ID: {self.session_id}")
        logger.info(f"[INIT] User ID: {self.user_id}")

        self.agent = self._create_agent()
        logger.info(f"[INIT] Agent created with model: gemini-2.5-flash")

        self.runner = InMemoryRunner(self.agent, app_name="BushidoGame")
        logger.info(f"[INIT] InMemoryRunner created")

    async def initialize_session(self):
        """Initialize the session asynchronously (must be called after __init__)"""
        logger.info(f"[INIT] Attempting to initialize session for {self.session_id}")

        if hasattr(self.runner, 'session_service'):
            if hasattr(self.runner.session_service, 'create_session'):
                try:
                    # create_session is async and requires app_name, user_id, and session_id
                    await self.runner.session_service.create_session(
                        app_name="BushidoGame",
                        user_id=self.user_id,
                        session_id=self.session_id
                    )
                    logger.info(f"[INIT] Session created successfully: {self.session_id}")
                except Exception as e:
                    logger.error(f"[INIT] Failed to create session: {type(e).__name__}: {e}")
                    import traceback
                    logger.error(f"[INIT] Traceback: {traceback.format_exc()}")
                    raise RuntimeError(f"Could not create session {self.session_id}: {e}") from e
            else:
                logger.error(f"[INIT] session_service does not have create_session method")
                raise RuntimeError("session_service does not support create_session")
        else:
            logger.error(f"[INIT] Runner does not have session_service attribute")
            raise RuntimeError("Runner does not have session_service")

    def _create_agent(self) -> Agent:
        """Create ADK agent with human-like reasoning"""

        # Personality-specific instructions
        persona_instructions = self._generate_persona_instructions()

        # Create tools with access to game state
        tools = create_player_tools(self.state, self.game_state)

        return Agent(
            name=f"Player_{self.state.persona.name}",
            model="gemini-2.5-flash",  # Using stable model for broader region availability
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
        # Create the prompt for this turn
        opponent = (self.game_state.defender if self.state.role == PlayerRole.CHALLENGER
                   else self.game_state.challenger)

        prompt = f"""
It's your turn in the duel! You are {self.state.persona.name}.

Current game state:
- Turn: {self.game_state.turn_number}
- Your health: {self.state.health}/3
- Opponent health: {opponent.health}/3

Use your tools to analyze the situation and make your decision.
Think through your options carefully, express your thoughts, and then provide your decision.
"""

        logger.info(f"[LLM] Requesting decision from {self.state.persona.name} (turn {self.game_state.turn_number})")

        # Create message
        message = types.Content(
            parts=[types.Part(text=prompt)]
        )

        # Run the agent
        full_response = ""
        event_count = 0

        try:
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=message
            ):
                event_count += 1

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_response += part.text

        except Exception as e:
            logger.error(f"[LLM] Error during runner.run_async: {type(e).__name__}: {e}")
            logger.error(f"[LLM] Session ID: {self.session_id}")
            logger.error(f"[LLM] User ID: {self.user_id}")
            logger.error(f"[LLM] Events received before error: {event_count}")
            raise

        logger.info(f"[LLM] {self.state.persona.name} completed reasoning ({len(full_response)} chars, {event_count} events)")
        logger.info(f"[LLM] Full response:\n{full_response}")

        if not full_response:
            logger.error(f"[LLM] Empty response received from agent after {event_count} events")
            raise RuntimeError(f"Empty response from LLM for {self.state.persona.name}")

        # Parse the decision from response
        decision = self._parse_decision(full_response)
        logger.info(f"[LLM] Parsed decision: actions={decision['actions']}, technique={decision['technique']}")

        # Update emotional state based on game situation
        observations = {
            "tension_level": decision["tension"],
            "opponent_health": opponent.health
        }
        MetricsTracker.update_emotional_state(self.state, observations)

        return decision

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

        # Calculate metrics for this decision using MetricsTracker
        metrics = MetricsTracker.calculate_decision_metrics(
            self.state, self.game_state, actions_tuple
        )

        return {
            "actions": actions_tuple,
            "technique": technique,
            "reasoning": reasoning,
            "deliberation": response,  # Full reasoning response
            **metrics
        }


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
            game_id=str(uuid4()),
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

        # Initialize sessions asynchronously
        await self.player_agents[PlayerRole.CHALLENGER].initialize_session()
        await self.player_agents[PlayerRole.DEFENDER].initialize_session()

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

        # Resolve turn using GameRulesEngine
        turn_result, new_position = GameRulesEngine.resolve_turn(
            self.game_state.turn_number,
            self.game_state.position,
            self.game_state.challenger,
            self.game_state.defender,
            challenger_decision,
            defender_decision
        )

        # Update position
        self.game_state.position = new_position

        # Update player resources using PlayerResourceManager
        PlayerResourceManager.update_both_players(
            self.game_state.challenger,
            self.game_state.defender,
            challenger_decision["actions"],
            defender_decision["actions"],
            turn_result["damage_dealt"]
        )

        # Log turn results
        self.logger.info(f"Turn {self.game_state.turn_number} Results:")
        self.logger.info(f"  Position: {turn_result['position_before']} -> {turn_result['position_after']}")
        self.logger.info(f"  Challenger actions: {[a.value for a in turn_result['challenger_actions']]}")
        self.logger.info(f"  Defender actions: {[a.value for a in turn_result['defender_actions']]}")
        self.logger.info(f"  Damage dealt - Challenger took: {turn_result['damage_dealt']['challenger']}, Defender took: {turn_result['damage_dealt']['defender']}")
        self.logger.info(f"  Health - Challenger: {self.game_state.challenger.health}, Defender: {self.game_state.defender.health}")
        if 'honor_violation' in turn_result:
            self.logger.warning(f"  HONOR VIOLATION: {turn_result['honor_violation']}")

        # Store turn in history
        self.game_state.turn_history.append(turn_result)

        # Record psychological metrics using MetricsTracker
        MetricsTracker.record_turn_metrics(
            self.game_state,
            challenger_decision,
            defender_decision
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

    def check_victory(self) -> Optional[str]:
        """Check for victory conditions using GameRulesEngine"""
        last_turn = self.game_state.turn_history[-1] if self.game_state.turn_history else None
        return GameRulesEngine.check_victory(
            self.game_state.challenger,
            self.game_state.defender,
            last_turn
        )

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

    async def _run_single_simulation(self, sim_id: int,
                                    personas: Tuple[PlayerPersona, PlayerPersona]) -> Dict[str, Any]:
        """Run a single game simulation"""

        logger.info(f"Simulation {sim_id}: {personas[0].name} vs {personas[1].name}")

        gm = GameMasterAgent(f"sim_{sim_id}")
        await gm.initialize_game(personas)

        # Run game until completion
        for turn in range(MAX_TURNS):
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
