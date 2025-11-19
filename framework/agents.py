import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from .interface import GameInterface

logger = logging.getLogger(__name__)

class PlaytestPlayerAgent:
    """
    Generic player agent using reasoning chains
    Works with any game implementing GameInterface
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


class GameMasterAgent:
    """
    Root agent that manages game flow
    Works with any game implementing GameInterface
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
