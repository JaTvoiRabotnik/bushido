"""
Generic Playtesting Agent System
Works with any game implementing the GameInterface

Based on patterns from "Agentic Design Patterns" book:
- Chapter 3: Parallelization (page 32) - for running multiple game simulations
- Chapter 17: Reasoning Techniques (page 241) - for player decision-making
- Chapter 20: Prioritization (page 310) - for strategic choices
- Memory patterns for adaptive strategy
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import vertexai

from game_interface import GameInterface


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


# ==================== PLAYER AGENT ====================

class PlaytestPlayerAgent:
    """
    Generic player agent using reasoning chains
    Works with any game implementing GameInterface
    Based on Chapter 17: Reasoning Techniques (page 241-261)
    """

    def __init__(self, player_state: Any, game_state: Any, game: GameInterface, player_index: int):
        self.state = player_state
        self.game_state = game_state
        self.game = game
        self.player_index = player_index

        # Use generic session IDs
        self.session_id = f"game_{game_state.game_id}_player{player_index}"
        self.user_id = f"player_{player_state.persona.name}"

        logger.info(f"[INIT] Creating agent for {player_state.persona.name} (Player {player_index})")
        logger.info(f"[INIT] Session ID: {self.session_id}")
        logger.info(f"[INIT] User ID: {self.user_id}")

        self.agent = self._create_agent()
        logger.info(f"[INIT] Agent created with model: gemini-2.5-flash")

        self.runner = InMemoryRunner(self.agent, app_name=game.get_game_name().replace(" ", ""))
        logger.info(f"[INIT] InMemoryRunner created")

    async def initialize_session(self):
        """Initialize the session asynchronously (must be called after __init__)"""
        logger.info(f"[INIT] Attempting to initialize session for {self.session_id}")

        if hasattr(self.runner, 'session_service'):
            if hasattr(self.runner.session_service, 'create_session'):
                try:
                    # create_session is async and requires app_name, user_id, and session_id
                    await self.runner.session_service.create_session(
                        app_name=self.game.get_game_name().replace(" ", ""),
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

        # Get game-specific instructions
        instruction = self.game.get_agent_instruction(self.state)

        # Create game-specific tools
        tools = self.game.create_player_tools(self.state, self.game_state)

        return Agent(
            name=f"Player_{self.state.persona.name}",
            model="gemini-2.5-flash",  # Using stable model for broader region availability
            description=f"A {self.state.persona.personality.value} player in {self.game.get_game_description()}",
            instruction=instruction,
            tools=tools
        )

    async def get_decision_from_agent(self) -> Dict[str, Any]:
        """
        Invoke the agent via runner to get a decision
        Returns parsed decision with actions, technique, and reasoning
        """
        # Create the prompt for this turn
        opponent = self.game.get_opponent(self.game_state, self.state)

        # Generic prompt that works for any game
        prompt = f"""
It's your turn! You are {self.state.persona.name}.

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

        # Parse the decision using game-specific parser
        decision = self.game.parse_decision(full_response, self.state, self.game_state)
        logger.info(f"[LLM] Parsed decision: {decision.get('actions', 'N/A')}")

        # Update emotional state using game-specific logic
        opponent = self.game.get_opponent(self.game_state, self.state)
        self.game.update_emotional_state(self.state, decision, opponent)

        return decision


# ==================== GAME MASTER AGENT ====================

class GameMasterAgent:
    """
    Root agent that manages game flow
    Works with any game implementing GameInterface
    Pattern: Orchestrator (implied throughout book's multi-agent examples)
    """

    def __init__(self, simulation_id: str, game: GameInterface):
        self.simulation_id = simulation_id
        self.game = game
        self.game_state = None
        self.player_agents = {}
        self.logger = logging.getLogger(f"GameMaster_{simulation_id}")

    async def initialize_game(self, personas: tuple) -> Any:
        """Initialize a new game with given personas"""

        game_id = str(uuid4())

        # Initialize players using game-specific logic
        player1, player2 = self.game.initialize_players(personas, game_id)

        # Initialize game state using game-specific logic
        self.game_state = self.game.initialize_game_state(game_id, player1, player2)

        # Create player agents
        self.player_agents[0] = PlaytestPlayerAgent(
            player1, self.game_state, self.game, 0
        )
        self.player_agents[1] = PlaytestPlayerAgent(
            player2, self.game_state, self.game, 1
        )

        # Initialize sessions asynchronously
        await self.player_agents[0].initialize_session()
        await self.player_agents[1].initialize_session()

        self.logger.info(f"Game {self.game_state.game_id} initialized")
        return self.game_state

    async def run_turn(self) -> Dict[str, Any]:
        """Execute a single game turn"""

        self.game_state.turn_number += 1
        self.logger.info(f"Starting turn {self.game_state.turn_number}")

        # Get decisions from both players in parallel
        # Pattern: Parallelization (Chapter 3, page 32)
        player1_task = asyncio.create_task(
            self._get_player_decision(0)
        )
        player2_task = asyncio.create_task(
            self._get_player_decision(1)
        )

        player1_decision, player2_decision = await asyncio.gather(
            player1_task, player2_task
        )

        # Resolve turn using game-specific logic
        turn_result = self.game.resolve_turn(
            self.game_state,
            player1_decision,
            player2_decision
        )

        # Update game state using game-specific logic
        self.game.update_game_state(self.game_state, turn_result)

        # Log turn results
        self.logger.info(f"Turn {self.game_state.turn_number} Results:")
        self.logger.info(f"  Turn result: {turn_result}")

        # Record psychological metrics using game-specific logic
        self.game.record_turn_metrics(
            self.game_state,
            player1_decision,
            player2_decision
        )

        return turn_result

    async def _get_player_decision(self, player_index: int) -> Dict[str, Any]:
        """Get decision from player agent using LLM reasoning"""

        agent = self.player_agents[player_index]

        # Get decision from agent via LLM invocation
        decision = await agent.get_decision_from_agent()

        self.logger.info(f"Player {player_index} decision: {decision.get('actions', 'N/A')}")
        self.logger.info(f"  Reasoning: {decision.get('reasoning', 'N/A')}")
        self.logger.info(f"  Emotion: {agent.state.persona.emotional_state}")

        return decision

    def check_victory(self) -> Optional[str]:
        """Check for victory conditions using game-specific logic"""
        return self.game.check_victory(self.game_state)

    async def complete_game(self) -> Dict[str, Any]:
        """Complete the game and generate summary"""

        winner = self.check_victory()

        # Get game summary using game-specific logic
        summary = self.game.get_game_summary(self.game_state, winner)

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
    Works with any game implementing GameInterface
    Pattern: Parallelization (Chapter 3, page 32)
    """

    def __init__(self, game: GameInterface):
        self.game = game
        self.simulations = []
        self.results = []

    async def run_simulations(self, num_simulations: int) -> List[Dict[str, Any]]:
        """Run multiple game simulations in parallel"""

        logger.info(f"Starting {num_simulations} simulations")

        # Create diverse persona pairs using game-specific logic
        persona_pairs = self.game.generate_persona_pairs(num_simulations)

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

    async def _run_single_simulation(self, sim_id: int, personas: tuple) -> Dict[str, Any]:
        """Run a single game simulation"""

        logger.info(f"Simulation {sim_id}: {personas[0].name} vs {personas[1].name}")

        gm = GameMasterAgent(f"sim_{sim_id}", self.game)
        await gm.initialize_game(personas)

        # Run game until completion
        max_turns = self.game.get_max_turns()

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
            "player1": self.game.format_persona_for_summary(personas[0]),
            "player2": self.game.format_persona_for_summary(personas[1])
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

        # Generic balance analysis - works for games with "winner" field
        player1_wins = sum(1 for r in self.results if "CHALLENGER" in str(r.get("winner", "")).upper() or "PLAYER1" in str(r.get("winner", "")).upper())
        player2_wins = sum(1 for r in self.results if "DEFENDER" in str(r.get("winner", "")).upper() or "PLAYER2" in str(r.get("winner", "")).upper())
        draws = sum(1 for r in self.results if r.get("winner") == "DRAW")

        return {
            "player1_win_rate": player1_wins / len(self.results) if self.results else 0,
            "player2_win_rate": player2_wins / len(self.results) if self.results else 0,
            "draw_rate": draws / len(self.results) if self.results else 0,
            "average_game_length": sum(r["total_turns"] for r in self.results) / len(self.results) if self.results else 0,
        }

    def _analyze_engagement(self) -> Dict[str, Any]:
        """Analyze player engagement metrics"""

        return {
            "average_tension": sum(r.get("average_tension", 0) for r in self.results) / len(self.results) if self.results else 0,
            "average_choice_difficulty": sum(r.get("average_choice_difficulty", 0)
                                           for r in self.results) / len(self.results) if self.results else 0,
            "average_enjoyment": sum(r.get("average_enjoyment", 0) for r in self.results) / len(self.results) if self.results else 0,
            "high_tension_games": sum(1 for r in self.results if r.get("average_tension", 0) > 0.7) / len(self.results) if self.results else 0,
            "high_enjoyment_games": sum(1 for r in self.results if r.get("average_enjoyment", 0) > 0.7) / len(self.results) if self.results else 0
        }

    def _analyze_matchups(self) -> Dict[str, Dict[str, float]]:
        """Analyze personality matchup results"""

        matchup_data = {}

        for result in self.results:
            matchup_key = f"{result['personas']['player1']}_vs_{result['personas']['player2']}"

            if matchup_key not in matchup_data:
                matchup_data[matchup_key] = {
                    "games": 0,
                    "player1_wins": 0,
                    "total_enjoyment": 0,
                    "total_tension": 0
                }

            matchup_data[matchup_key]["games"] += 1
            if "CHALLENGER" in str(result.get("winner", "")).upper() or "PLAYER1" in str(result.get("winner", "")).upper():
                matchup_data[matchup_key]["player1_wins"] += 1
            matchup_data[matchup_key]["total_enjoyment"] += result.get("average_enjoyment", 0)
            matchup_data[matchup_key]["total_tension"] += result.get("average_tension", 0)

        # Calculate averages
        for matchup in matchup_data.values():
            if matchup["games"] > 0:
                matchup["win_rate"] = matchup["player1_wins"] / matchup["games"]
                matchup["avg_enjoyment"] = matchup["total_enjoyment"] / matchup["games"]
                matchup["avg_tension"] = matchup["total_tension"] / matchup["games"]

        return matchup_data

    def _generate_recommendations(self, balance: Dict, engagement: Dict) -> List[str]:
        """Generate recommendations for game improvement"""

        recommendations = []

        # Balance recommendations
        if abs(balance["player1_win_rate"] - 0.5) > 0.15:
            if balance["player1_win_rate"] > 0.5:
                recommendations.append("Consider buffing Player 2's starting position")
            else:
                recommendations.append("Consider buffing Player 1's starting position")

        # Engagement recommendations
        if engagement["average_tension"] < 0.5:
            recommendations.append("Games may be too predictable - consider adding more swing mechanics")

        if engagement["average_enjoyment"] < 0.6:
            recommendations.append("Player enjoyment is low - consider adding more meaningful choices")

        if engagement["average_choice_difficulty"] < 0.3:
            recommendations.append("Choices may be too obvious - consider balancing option values")

        if balance["average_game_length"] < 3:
            recommendations.append("Games ending too quickly - consider adjusting game length")
        elif balance["average_game_length"] > 7:
            recommendations.append("Games may be dragging - consider increasing pace")

        return recommendations if recommendations else ["Game appears well-balanced!"]


# ==================== MAIN EXECUTION ====================

async def main():
    """Main execution function"""

    # Import the specific game implementation
    from bushido_game import BushidoGame
    game = BushidoGame()

    # Initialize Vertex AI
    vertex_initialized = initialize_vertex_ai()
    if not vertex_initialized:
        print("\nWARNING: Running without Vertex AI. Set GOOGLE_CLOUD_PROJECT environment variable for LLM-powered agents.")
        print("The system will fall back to deterministic decision-making.\n")

    print("=" * 60)
    print(f"{game.get_game_name().upper()} - AUTOMATED PLAYTESTING SYSTEM")
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
    orchestrator = SimulationOrchestrator(game)

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
    print(f"  Player 1 Win Rate: {report['balance_metrics']['player1_win_rate']:.1%}")
    print(f"  Player 2 Win Rate: {report['balance_metrics']['player2_win_rate']:.1%}")
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
