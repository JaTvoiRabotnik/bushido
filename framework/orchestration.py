import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from .interface import GameInterface
from .agents import GameMasterAgent

logger = logging.getLogger(__name__)

class SimulationOrchestrator:
    """
    Main orchestrator for running multiple game simulations
    Works with any game implementing GameInterface
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
