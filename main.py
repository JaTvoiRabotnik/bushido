import asyncio
import logging
import os
import json
from datetime import datetime

from framework.runner import initialize_vertex_ai
from framework.orchestration import SimulationOrchestrator
from games.bushido.game import BushidoGame
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bushido_simulation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main execution function"""
    
    # Initialize Vertex AI
    # Try to get from environment if not in settings
    project_id = settings.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = settings.location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not initialize_vertex_ai(project_id, location):
        print("Failed to initialize Vertex AI. Please check your credentials and project ID.")
        return

    # Initialize game
    game = BushidoGame()
    
    # Initialize orchestrator
    orchestrator = SimulationOrchestrator(game)
    
    print("\n=== Bushido Card Game Simulation Framework ===")
    print("Based on 'Agentic Design Patterns' by Google Cloud\n")
    
    try:
        num_sims = int(input("Enter number of simulations to run (default 1): ") or "1")
    except ValueError:
        num_sims = 1
        
    print(f"\nStarting {num_sims} simulations...")
    
    # Run simulations
    results = await orchestrator.run_simulations(num_sims)
    
    # Generate report
    report = await orchestrator.generate_evaluation_report()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("simulation_results", exist_ok=True)
    
    results_file = f"simulation_results/sim_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
        
    report_file = f"simulation_results/report_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\nSimulations complete!")
    print(f"Results saved to {results_file}")
    print(f"Report saved to {report_file}")
    
    # Print summary
    print("\n=== Summary Report ===")
    print(f"Total Games: {report['total_simulations']}")
    print(f"Player 1 Win Rate: {report['balance_metrics']['player1_win_rate']:.2%}")
    print(f"Player 2 Win Rate: {report['balance_metrics']['player2_win_rate']:.2%}")
    print(f"Draw Rate: {report['balance_metrics']['draw_rate']:.2%}")
    print(f"Avg Game Length: {report['balance_metrics']['average_game_length']:.1f} turns")
    print(f"Avg Enjoyment: {report['engagement_metrics']['average_enjoyment']:.2f}/1.0")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(main())
