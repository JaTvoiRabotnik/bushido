# Bushido Card Game Testing Agent System

An advanced multi-agent system for automated playtesting of card games, featuring human-like reasoning and emotional simulation. Built with Google ADK (Agent Development Kit) and designed for deployment on Google Vertex AI.
## 📚 Architecture

The system is built on a modular architecture separating the agent framework from game logic:

### 1. Framework Layer (`framework/`)
- **Agents**: Generic `PlaytestPlayerAgent` and `GameMasterAgent`
- **Orchestration**: `SimulationOrchestrator` for managing batches
- **Interface**: `GameInterface` abstract base class
- **Adapter**: `GameAgentAdapter` for decoupling game logic from agents

### 2. Game Layer (`games/bushido/`)
- **Game Logic**: `BushidoGame` implementation
- **Rules Engine**: `GameRulesEngine` with stateless logic
- **Models**: Pydantic models for structured data
- **Tools**: Stateless tool definitions for agents

### 3. Configuration (`config/`)
- Centralized settings for agents and simulation parameters

## 🎮 System Components

### 1. **GameMasterAgent**
- Manages game rules and state
- Resolves turns according to Bushido rules
- Tracks victory conditions
- Logs all game events for analysis

### 2. **BushidoPlayerAgent**
- Simulates human-like players with personalities
- Features emotional states and confidence levels
- Implements strategy memory and learning
- Makes decisions through reasoning chains

### 3. **SimulationOrchestrator**
- Coordinates multiple game simulations
- Runs games in parallel batches
- Generates comprehensive evaluation reports
- Analyzes balance and engagement metrics

### 4. **EvaluatorAgent** (Implicit in reporting)
- Analyzes game balance metrics
- Measures player engagement and tension
- Generates improvement recommendations
- Tracks personality matchup effectiveness

## 🧠 Human-Like Player Simulation

### Personality Traits
- **Aggressive**: Prefers offensive tactics, gets frustrated when defending
- **Defensive**: Prioritizes survival, finds satisfaction in successful blocks
- **Adaptive**: Reads patterns and adjusts strategy dynamically
- **Calculated**: Focuses on mathematical optimization
- **Unpredictable**: Varies tactics to confuse opponents
- **Honorable**: Values style over pure victory

### Psychological Factors
- **Emotional States**: calm, focused, tense, desperate, excited
- **Confidence Levels**: Dynamically adjust based on game state
- **Tension Tracking**: Measures pressure felt during decisions
- **Enjoyment Scoring**: Tracks fun factor of different situations

### Decision-Making Process
1. **Situation Analysis**: Read game state and opponent patterns
2. **Option Evaluation**: Consider multiple moves with reasoning
3. **Emotional Response**: React to options based on personality
4. **Risk Assessment**: Calculate perceived danger of actions
5. **Final Decision**: Choose with human-like deliberation

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Google Cloud Project
- Google AI API Key (for Gemini model access)

### Local Development Setup

1. **Clone the repository**
```bash
git clone [your-repo-url]
cd bushido-testing-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_AI_API_KEY="your-api-key"  # Or use Secret Manager
export GOOGLE_CLOUD_LOCATION="us-central1"  # Optional
```

4. **Run locally**
```bash
python main.py
```

### Production Deployment (Vertex AI)

1. **Configure environment**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export RESULTS_BUCKET="your-gcs-bucket"
export SERVICE_ACCOUNT="your-sa@project.iam.gserviceaccount.com"  # Optional
```

2. **Run deployment script**
```bash
./deploy.sh
```

3. **Deploy to Vertex AI**
```python
from vertex_ai_config import deploy_to_vertex_ai
deploy_to_vertex_ai()
```

## 🔐 Security Best Practices

### Secret Management
- **Never store API keys in code or config files**
- Use environment variables for local development
- Use Google Secret Manager for production
- Implement service accounts with minimal permissions

### Deployment Security
- Use VPC Service Controls for network isolation
- Enable Customer-Managed Encryption Keys (CMEK) if required
- Implement proper IAM roles and permissions
- Regular security audits of dependencies

## 📊 Output and Analysis

### Simulation Results
Each simulation generates:
- Turn-by-turn game logs
- Player reasoning traces
- Emotional state transitions
- Strategic decision records

### Evaluation Metrics
- **Balance Metrics**: Win rates, game length, health differentials
- **Engagement Metrics**: Tension levels, choice difficulty, enjoyment scores
- **Matchup Analysis**: Personality combination effectiveness
- **Recommendations**: AI-generated improvement suggestions

### Result Storage
- Local: `./simulation_results/` directory
- Cloud: GCS bucket with configurable prefix
- Format: JSON for machine processing

## 🔧 Configuration

### Core Settings (vertex_ai_config.py)
```python
# Model Configuration
model_name = "gemini-2.0-flash"
temperature = 0.7  # Human-like variation

# Simulation Configuration
max_parallel_games = 5
max_turns_per_game = 10
default_simulation_count = 10

# Agent Configuration
enable_reasoning_traces = True
enable_emotion_tracking = True
enable_strategy_memory = True
```

## 📈 Extending the System

### Adding New Games
1. Create new rule resolution module
2. Define game-specific state classes
3. Implement position/combat mechanics
4. Update technique/card systems

### Adding Personality Types
1. Define new PersonalityTrait enum
2. Create personality-specific instructions
3. Implement scoring modifiers
4. Add emotional responses

### Custom Evaluation Metrics
1. Extend evaluation report generation
2. Add new metric calculations
3. Implement custom recommendations
4. Create visualization tools

## 🤝 Contributing

We welcome contributions! Key areas for improvement:
- Additional personality types
- More sophisticated learning algorithms
- Enhanced pattern recognition
- Visualization dashboards
- Support for more game types

## 📄 License

MIT License

## 🙏 Acknowledgments

- Based on patterns from "Agentic Design Patterns" by Antonio Gullì
- Built with Google ADK (Agent Development Kit)
- Powered by Google Gemini models

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact: marco@wayji.com

---

**Note**: This system is designed for game balance testing and uses AI to simulate human-like gameplay. The emotional states and personalities are simulations for testing purposes and do not represent actual human psychology.
