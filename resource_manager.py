"""
Player resource management for Bushido Card Game
Handles health, momentum, and balance operations
"""

from typing import Tuple
from models import PlayerState, ActionCard
from constants import MAX_MOMENTUM, MAX_BALANCE


class PlayerResourceManager:
    """
    Centralized resource management for player states
    Eliminates duplication from original update logic
    """

    @staticmethod
    def adjust_momentum(player: PlayerState, amount: int, cap: int = MAX_MOMENTUM) -> None:
        """Adjust momentum with bounds checking"""
        player.momentum = max(0, min(cap, player.momentum + amount))

    @staticmethod
    def adjust_balance(player: PlayerState, amount: int, cap: int = MAX_BALANCE) -> None:
        """Adjust balance with bounds checking"""
        player.balance = max(0, min(cap, player.balance + amount))

    @staticmethod
    def take_damage(player: PlayerState, amount: int) -> None:
        """Apply damage to player health"""
        player.health = max(0, player.health - amount)

    @staticmethod
    def apply_action_effects(player: PlayerState, actions: Tuple[ActionCard, ...]) -> None:
        """
        Apply resource changes based on player actions
        Replaces duplicated update logic from original code (lines 957-984)
        """
        has_movement = False

        for action in actions:
            if action == ActionCard.ADVANCE:
                PlayerResourceManager.adjust_momentum(player, +1)
                PlayerResourceManager.adjust_balance(player, -1)
                has_movement = True
            elif action == ActionCard.RETREAT:
                PlayerResourceManager.adjust_momentum(player, -1)
                has_movement = True

        # If player stayed (no movement action), gain balance
        if not has_movement and actions:
            PlayerResourceManager.adjust_balance(player, +1)

    @staticmethod
    def update_both_players(
        challenger: PlayerState,
        defender: PlayerState,
        challenger_actions: Tuple[ActionCard, ...],
        defender_actions: Tuple[ActionCard, ...],
        damage_dealt: dict
    ) -> None:
        """
        Update both players' resources after turn resolution
        Centralizes the duplicated update logic
        """
        # Apply damage
        PlayerResourceManager.take_damage(challenger, damage_dealt["challenger"])
        PlayerResourceManager.take_damage(defender, damage_dealt["defender"])

        # Apply action effects
        PlayerResourceManager.apply_action_effects(challenger, challenger_actions)
        PlayerResourceManager.apply_action_effects(defender, defender_actions)
