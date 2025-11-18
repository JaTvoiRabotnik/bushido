"""
Game constants for Bushido Card Game
Technique cards and other game configuration
"""

from typing import Dict, Any


# ==================== TECHNIQUE CARDS ====================

TECHNIQUE_CARDS: Dict[str, Dict[str, Any]] = {
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


# ==================== GAME CONFIGURATION ====================

DEFAULT_HEALTH = 3
DEFAULT_MOMENTUM = 0
DEFAULT_BALANCE = 0
MAX_MOMENTUM = 3
MAX_BALANCE = 3
MAX_TURNS = 10  # Safety limit for simulations
HONOR_RESTRICTION_TURN = 3  # Turn after which retreat is forbidden
