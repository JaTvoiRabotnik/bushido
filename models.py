"""
Data models for Bushido Card Game
Enums, dataclasses, and game state structures
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum


# ==================== ENUMS ====================

class Position(Enum):
    """Game position states"""
    APART = "Apart"
    SWORD = "Sword Range"
    CLOSE = "Close Combat"


class ActionCard(Enum):
    """Available action cards"""
    ATTACK = "Attack"
    DEFEND = "Defend"
    ADVANCE = "Advance"
    RETREAT = "Retreat"
    INSIGHT = "Insight"


class PlayerRole(Enum):
    """Player roles in the game"""
    CHALLENGER = "Challenger"
    DEFENDER = "Defender"


class PersonalityTrait(Enum):
    """
    Player personality types
    Based on persona-based agents (Agentic Design Patterns, page 372)
    """
    AGGRESSIVE = "Aggressive - Prefers offensive tactics"
    DEFENSIVE = "Defensive - Prioritizes survival"
    ADAPTIVE = "Adaptive - Changes strategy based on opponent"
    CALCULATED = "Calculated - Focuses on optimal plays"
    UNPREDICTABLE = "Unpredictable - Varies tactics to confuse"
    HONORABLE = "Honorable - Values style over pure victory"


# ==================== PLAYER MODELS ====================

@dataclass
class PlayerPersona:
    """
    Human-like persona for believable simulation
    Removed unused fields: learning_rate, enjoyment_factors
    """
    name: str
    personality: PersonalityTrait
    risk_tolerance: float  # 0.0 (cautious) to 1.0 (reckless)
    emotional_state: str = "calm"
    confidence_level: float = 0.5
    tension_threshold: float = 0.7  # When they feel pressure

    def describe(self) -> str:
        """Generate a human-like internal monologue"""
        return f"{self.name} ({self.personality.value}): {self.emotional_state}, confidence: {self.confidence_level:.2f}"


@dataclass
class PlayerState:
    """
    Complete state of a player
    Removed unused fields: known_attributes, strategy_log
    """
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

    def __post_init__(self):
        if not self.action_cards:
            self.action_cards = list(ActionCard)


@dataclass
class GameState:
    """Complete game state"""
    game_id: str
    turn_number: int = 0
    position: Position = Position.APART

    # Players
    challenger: Optional[PlayerState] = None
    defender: Optional[PlayerState] = None

    # History for analysis
    turn_history: List[Dict[str, Any]] = field(default_factory=list)

    # Metrics for evaluation
    tension_levels: List[float] = field(default_factory=list)
    choice_difficulty: List[float] = field(default_factory=list)
    enjoyment_scores: List[float] = field(default_factory=list)

    def get_player(self, role: PlayerRole) -> PlayerState:
        """Get player by role"""
        return self.challenger if role == PlayerRole.CHALLENGER else self.defender
