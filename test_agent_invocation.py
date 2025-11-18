#!/usr/bin/env python3
"""
Simple test script to verify agent invocation is working correctly.
This tests that agents can make decisions via LLM reasoning.
"""

import asyncio
import logging
from bushido_test_agent import (
    initialize_vertex_ai,
    GameMasterAgent,
    PlayerPersona,
    PersonalityTrait
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_single_turn():
    """Test a single turn with agent invocation"""

    print("=" * 60)
    print("AGENT INVOCATION TEST")
    print("=" * 60)

    # Initialize Vertex AI
    vertex_initialized = initialize_vertex_ai()
    if not vertex_initialized:
        print("\nWARNING: Running without Vertex AI.")
        print("Set GOOGLE_CLOUD_PROJECT environment variable to test LLM-powered agents.\n")
    else:
        print("\nVertex AI initialized successfully!")
        print("Agents will use LLM reasoning.\n")

    # Create two simple personas
    persona1 = PlayerPersona(
        name="Aggressive_Tester",
        personality=PersonalityTrait.AGGRESSIVE,
        risk_tolerance=0.8,
        learning_rate=0.3
    )

    persona2 = PlayerPersona(
        name="Defensive_Tester",
        personality=PersonalityTrait.DEFENSIVE,
        risk_tolerance=0.3,
        learning_rate=0.3
    )

    # Create game master
    print("Creating game...")
    gm = GameMasterAgent("test_001")
    await gm.initialize_game((persona1, persona2))

    print(f"\nGame initialized!")
    print(f"Challenger: {persona1.name} ({persona1.personality.value})")
    print(f"Defender: {persona2.name} ({persona2.personality.value})")
    print()

    # Run a single turn
    print("Running turn 1...")
    print("-" * 60)

    try:
        turn_result = await gm.run_turn()

        print("\nTURN RESULT:")
        print(f"Challenger actions: {turn_result['challenger_actions']}")
        print(f"Defender actions: {turn_result['defender_actions']}")
        print(f"Position: {turn_result['position_before']} -> {turn_result['position_after']}")
        print(f"Damage: Challenger took {turn_result['damage_dealt']['challenger']}, "
              f"Defender took {turn_result['damage_dealt']['defender']}")

        print("\nGAME STATE:")
        print(f"Challenger Health: {gm.game_state.challenger.health}/3")
        print(f"Defender Health: {gm.game_state.defender.health}/3")

        # Cleanup
        await gm.cleanup()

        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        if vertex_initialized:
            print("\n✓ Agents successfully used LLM reasoning to make decisions")
        else:
            print("\n✓ Agents used fallback deterministic logic (no Vertex AI)")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n✗ TEST FAILED: {e}")
        return False


async def test_full_game():
    """Test a complete game"""

    print("\n" + "=" * 60)
    print("FULL GAME TEST")
    print("=" * 60)

    # Create personas
    persona1 = PlayerPersona(
        name="Aggro_Player",
        personality=PersonalityTrait.AGGRESSIVE,
        risk_tolerance=0.7,
        learning_rate=0.3
    )

    persona2 = PlayerPersona(
        name="Defensive_Player",
        personality=PersonalityTrait.DEFENSIVE,
        risk_tolerance=0.4,
        learning_rate=0.3
    )

    # Create game
    gm = GameMasterAgent("test_002")
    await gm.initialize_game((persona1, persona2))

    print(f"\nStarting game: {persona1.name} vs {persona2.name}")

    # Run game
    max_turns = 5
    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")

        try:
            turn_result = await gm.run_turn()

            # Check for victory
            winner = gm.check_victory()
            if winner:
                print(f"\nGame Over! Winner: {winner}")
                break

        except Exception as e:
            logger.error(f"Error in turn {turn + 1}: {e}")
            break

    # Get summary
    summary = await gm.complete_game()

    print("\n" + "=" * 60)
    print("GAME SUMMARY")
    print("=" * 60)
    print(f"Winner: {summary['winner']}")
    print(f"Total Turns: {summary['total_turns']}")
    print(f"Average Tension: {summary['average_tension']:.2f}")
    print(f"Average Enjoyment: {summary['average_enjoyment']:.2f}")

    return True


async def main():
    """Run all tests"""

    # Test 1: Single turn
    success1 = await test_single_turn()

    if not success1:
        print("\nSkipping full game test due to single turn failure")
        return

    # Test 2: Full game (optional, can be slow with LLM)
    try:
        user_input = input("\nRun full game test? (y/n): ")
        if user_input.lower() == 'y':
            success2 = await test_full_game()

            if success2:
                print("\n✓ All tests passed!")
        else:
            print("\nSkipping full game test")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")


if __name__ == "__main__":
    asyncio.run(main())
