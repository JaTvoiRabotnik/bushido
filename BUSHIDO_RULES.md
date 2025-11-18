# Untitled Dueling Game - Rules Draft

## Overview
A 2-player card-driven tactical combat game where players engage in a duel lasting 3-5 turns. Victory is achieved by landing a successful attack on your opponent, with most attacks being fatal or nearly fatal.

## Setup
- **Determine Roles**: The Challenger and the Defender are chosen randomly.
- Each player has:
  - **5 Action Cards**: Attack, Defend, Advance, Retreat, Insight (held in hand throughout).
  - **2 Technique Cards**: 2 cards representing special abilities or fighting styles.
  - **14 initiative tokens**: Values from 1 to 7, one set for each player.
  - **3 Range Tokens**: Apart, Sword, Close. Game starts at **Apart** range (the furthest position).
  - **6 Evade Tokens**: Used to mark the turns where Attacks were successfully Evaded.
  - **Character Attributes**: Secret values for Speed, Strength, Defense (sum to 6).
- There are 10 Technique cards available. Remove 1 random card. Then the Challenger chooses 1 card, and passes the deck to the Defender. The Defender chooses 1 card, discards 2 card randomly, and passes the deck back to the Challenger. The Challenger then chooses another card, discards 1 card, and passes the deck back to the Defender. Finally the Defender chooses 1 more card, and discards the remaining cards in the deck. 
- **Starting Resources**:
  - Challenger begins with 1 Momentum, 0 Balance, 3 Health Points.
  - Defender begins with 0 Momentum, 1 Balance, 3 Health Points.

### Roles and Honor Conditions
**Challenger** (Aggressor):
- Starting advantage: 1 Momentum (ready to strike).

**Defender** (Respondent):
- Starting advantage: 1 Balance (composed and ready).

**Honor Condition**: If a player uses the Retreat card after Turn 3, they lose immediately by dishonor.

### Character Attributes
Each player distributes 6 points across three hidden attributes:
- **Speed**: Determines initiative for evade resolution (Speed + Current Balance).
- **Strength**: Base attack damage bonus.
- **Defense**: Base damage reduction.
- **Point Distribution**: Speed + Strength + Defense = 6 (minimum 1, maximum 4 in any single attribute).

Example builds:
- Balanced Fighter: Speed 2, Strength 2, Defense 2
- Glass Cannon: Speed 1, Strength 4, Defense 1
- Defensive Specialist: Speed 3, Strength 1, Defense 2
- Tank: Speed 1, Strength 2, Defense 3

### The Three Ranges
1. **Apart**: Players cannot attack each other (but can use Insight).
2. **Sword Range**: Players can perform normal attacks.
3. **Close Combat**: Players can perform normal attacks and perform special close-range attacks (technique dependent).

## Turn Structure

### 1. Simultaneous Action Selection
Each player secretly chooses their actions for the turn by selecting cards:
- **0, 1, or 2 Action Cards**: 
  - None (Stay Put)
  - One Movement card only (Advance or Retreat)
  - One Insight card only
  - One Combat card only (Attack or Defend) - only valid if resulting Movement will be in range
  - Two cards: one Movement (Advance/Retreat) + one Combat (Attack/Defend)
  - Two cards: one Movement (Advance/Retreat) + one Insight

- **Technique Card**: Played face-down


### 2. Simultaneous Reveal
All players reveal their chosen cards simultaneously.

### 3. Resolution

#### Position Resolution

##### Honor Condition Checks
- First, check for honor violation: Whomever played a Retreat card in turn 4 or later → Immediate loss by dishonor.
- If both players Retreat simultaneously, it's a draw.

Positions are resolved before combat based on the three-range system:

**From Apart:**
- Both Advance → Move to Sword Range
- One Advances, One Stays → Move to Sword Range
- One Advances, One Retreats → Remain at Apart
- Both Stay → Remain at Apart
- Both Retreat → Remain at Apart (cannot move further)
- One Retreats, One Stays → Remain at Apart

**From Sword Range:**
- Both Advance → Move to Close Combat
- One Advances, One Stays → Move to Close Combat
- One Advances, One Retreats → Remain at Sword Range
- Both Stay → Remain at Sword Range
- Both Retreat → Move to Apart
- One Retreats, One Stays → Move to Apart

**From Close Combat:**
- Both Advance → Remain at Close Combat (cannot move closer)
- One Advances, One Stays → Remain at Close Combat (cannot move closer)
- One Advances, One Retreats → Remain at Close Combat
- Both Stay → Remain at Close Combat
- Both Retreat → Move to Apart
- One Retreats, One Stays → Move to Sword Range

**After resolving position, change the Position token to represent the new Position**

#### Momentum & Balance Updates
- **Advance**: +1 Momentum, -1 Balance
- **Retreat**: -1 Momentum
- **Stay Put**: +1 Balance
- **Resource Caps**: Both Momentum and Balance are capped at 3 (some techniques may modify this cap)
- Resources cannot go below 0

#### Insight Resolution
If a player plays the Insight card (instead of attacking/defending):
- They gain insight into one hidden element of their opponent (player's choice):
  - **Speed attribute** value (persists for remainder of game)
  - **Strength attribute** value (persists for remainder of game)
  - **Defense attribute** value (persists for remainder of game)
  - **Current Technique Card** (reveals current card, and only if opponent is Attacking or Defending; opponent may change it next turn)
- If both players play Insight, both gain information
- **Vulnerability**: A player gaining insight is defenseless. If the opponent is in range and attacks, the insight-gaining player cannot defend and takes full damage (Attack Total with no Defense reduction). Their Technique card might still allow them to evade the Attack.

#### Combat Resolution
If players are at Sword Range or Close Combat and at least one chose to Attack:

1. **Reveal Technique Cards**: Players who are Attacking or Defending reveal their technique cards simultaneously.

2. **Activate Techniques**: Techniques activate based on their trigger conditions:
   - Attack techniques: Modify attack calculations
   - Defense techniques: Modify defense calculations or enable evasion
   - Movement techniques: Apply changes due to movement as per the technique card

3. **Apply Bonuses**:
   - **Advance**: +1 Attack bonus
   - **Retreat**: +1 Defense bonus
   - **Close Combat**: +1 Attack bonus (stacks with Advance if applicable)
   - Technique cards may convert Momentum or Balance into bonuses
   - Some techniques have special effects at Close Combat

4. **Calculate Total Values**:
   - Each player calculates their total:
     - **Attack Total** = Strength attribute + Technique bonuses + Position bonuses
     - **Defense Total** = Defense attribute + Technique bonuses + Position bonuses

5. **Calculate Damage**:
   - **Determine Evade Priority**: Each player calculates their Initiative = Speed + Current Balance
   - **Resolve Evades in Initiative Order** (highest first):
     - Player with higher Initiative declares evade attempt first
     - If evade succeeds (pays cost, meets conditions), they take no damage
     - Lower Initiative player then declares evade attempt
     - If Initiative is tied, evades resolve simultaneously
   - **Calculate Final Damage**: 
     - For each attacker whose attack was not evaded: **Damage = Attack Total - Defense Total** (minimum 0)
     - Attacks can deal up to ~5 damage
     - Undefended attacks are typically fatal (3 health vs 5 damage)

6. **Resolve Damage & Determine Outcome**:
   - Damage is applied simultaneously to both players
   - Players lose Health Points equal to damage taken
   - Techniques may allow evasion (take no damage while opponent does)
   - When a player reaches 0 Health Points, they are defeated
   - If both reach 0 simultaneously, the game is a draw

### 4. Between Turns
- Players may change their Technique Card selection for the next turn (from their 2 available technique cards)
- Revealed attribute information (Speed, Strength, Defense) remains known
- Current Momentum and Balance values persist

## Victory Conditions
- Reduce your opponent to 0 Health Points
- Players start with 3 Health Points
- Typical damage ranges:
  - Undefended attack: 4-8 damage (usually fatal)
  - Defended exchange: 1-3 damage per player
  - Perfect evade: 0 damage
- Most duels conclude in 2-4 turns
- If both players reach 0 HP simultaneously, the duel is a draw

## Sample Technique Cards

### **Tsubame Gaeshi (Swallow Reversal)**
*A lightning-fast double strike that exploits forward momentum*
- **Type**: Aggressive Momentum
- **Attack Effect**: +1 Attack damage per Momentum (spend all Momentum)
- **Evade Cost**: Spend 3 Momentum to evade one attack
- **Special**: At Close Combat, attacks bypass defense if you have 3 Momentum
- **Philosophy**: Overwhelming speed through committed aggression

### **Mizu no Kokoro (Mind Like Water)**
*Perfect defensive stillness and clarity*
- **Type**: Defensive Balance
- **Defense Effect**: +1 Defense per Balance (spend all Balance)
- **Evade Cost**: Spend 3 Balance to evade one attack
- **Special**: At Sword Range, attacks bypass evasion if you have 3 Balance
- **Philosophy**: Unshakeable composure in stillness

### **Kuzushi (Breaking Balance)**
*An aggressive technique that disrupts the opponent's stance*
- **Type**: Aggressive Disruption
- **Attack Effect**: +2 Attack when Advancing, steal 1 Balance from opponent on hit
- **Evade Cost**: Spend 3 Balance to evade (difficult for aggressive style)
- **Special**: Your attacks bypass evades that cost Balance
- **Philosophy**: Destroy the opponent's foundation

### **Ai-Uchi (Mutual Strike)**
*Accepting death to guarantee killing your opponent*
- **Type**: Sacrificial
- **Attack Effect**: Your attack ignores all Defense and Evades
- **Evade Cost**: Cannot evade (no evade capability)
- **Special**: You cannot defend on turns you use this technique
- **Philosophy**: Victory through mutual destruction

### **Irimi (Entering)**
*Stepping inside the opponent's reach to nullify their power*
- **Type**: Close Combat Specialist
- **Movement Effect**: When Advancing to Close Combat, gain +2 Balance
- **Evade Cost**: Spend 2 Momentum to evade at Close Combat
- **Special**: At Close Combat, opponent's Momentum bonuses are halved (rounded down)
- **Philosophy**: Control through proximity

### **Ma-ai (Distancing)**
*Masterful control of engagement range*
- **Type**: Range Control
- **Defense Effect**: +2 Defense when Retreating
- **Evade Cost**: Spend 1 Balance to evade when at Sword Range or further
- **Special**: When Retreating, lose only 1 Momentum instead of all Momentum
- **Philosophy**: Safety through perfect spacing

### **Sen Sen no Sen (Before Before Initiative)**
*Striking the moment before your opponent commits*
- **Type**: Anticipation
- **Attack Effect**: +1 Attack per opponent's Momentum (maximum +3)
- **Evade Cost**: Spend Balance equal to opponent's Momentum to evade
- **Special**: If your Balance exceeds opponent's Momentum by 2+, bypass their Momentum-based evades
- **Philosophy**: Punish aggression with preparation

### **Mushin (No-Mind)**
*Spontaneous action without conscious thought*
- **Type**: Zen Emptiness
- **Attack/Defense Effect**: +3 to Attack or Defense if you have 0 Momentum AND 0 Balance
- **Evade Cost**: Free evade if you have exactly 0 Momentum and 0 Balance
- **Special**: Reset both Momentum and Balance to 0 at start of any turn (optional)
- **Philosophy**: Power in emptiness

### **Nagashi (Flowing Parry)**
*Redirecting the opponent's force*
- **Type**: Counter-fighter
- **Defense Effect**: +1 Defense, gain Momentum equal to damage prevented (maximum +2)
- **Evade Cost**: Spend 2 Momentum to evade and immediately gain 1 Balance
- **Special**: If opponent attacks with 5 damage, you may spend 3 Balance to fully evade and counter for 2 damage
- **Philosophy**: Turn defense into offense

### **Koboichi (Attack and Defense as One)**
*The principle that true defense is counterattack*
- **Type**: Counter-striker
- **Defense Effect**: When Defending, deal damage equal to your Defense ÷ 2 (rounded down) to attacker
- **Evade Cost**: Spend 4 Balance to evade an attack and counter for 3 damage
- **Special**: Cannot be bypassed by momentum-based attacks
- **Philosophy**: There is no pure defense

### **Tsuki-kage (Moon Shadow)**
*Deceptive movement in half-light*
- **Type**: Feint Specialist
- **Attack Effect**: +1 Attack, opponent must spend +1 additional resource to evade
- **Evade Cost**: Spend 1 Momentum OR 1 Balance to evade (your choice)
- **Special**: Your evades cannot be bypassed by techniques that require "greater than" comparisons
- **Philosophy**: Unpredictability is strength

### **Fudoshin (Immovable Mind)**
*Unshakeable resolve and presence*
- **Type**: Tank/Fortress
- **Defense Effect**: +2 Defense when you Stay Put
- **Evade Cost**: Cannot evade (but difficult to damage)
- **Special**: Immune to Balance-stealing effects, maximum Balance cap increased to 6
- **Philosophy**: The mountain does not move

---

## Design Notes & Open Questions
1. **Technique Card Count**: 2 technique cards per player
2. **Technique Swapping**: Players may swap technique at the start of each turn (before action selection)
3. **Initiative Ties**: When Speed + Balance equals, compare raw Speed; if still tied, resolve simultaneously
4. **Insight Mechanics**: Insight reveals one attribute of the acting player's choice (Speed, Strength, Defense, or current Technique)
5. **Starting Position**: Both players always start Apart

## Quick Reference

### Common Calculations
**Attack Total** = Strength + Technique bonuses + Position bonuses (Advance +1, Close Combat +1)
**Defense Total** = Defense + Technique bonuses + Position bonuses (Retreat +1)
**Initiative** = Speed + Current Balance
**Final Damage** = Attack Total - Defense Total (minimum 0, if not evaded)

### Typical Turn Sequence
1. Select action cards (0-2) + technique card
2. Reveal action cards simultaneously
3. Resolve position changes
4. Update Momentum/Balance
5. Reveal techniques (if combat)
6. Calculate totals, place tokens
7. Determine initiative (Speed + Balance)
8. Resolve evades (highest initiative first)
9. Apply damage
10. Check for victory

### Resource Summary
- **Momentum**: Gained by Advancing (+1), lost by Retreating (-1). Capped at 3.
  - Challenger starts with 1 Momentum
- **Balance**: Gained by Staying Put (+1), lost by Advancing (-1). Capped at 3.
  - Defender starts with 1 Balance
- **Health**: Start at 3, lose when taking damage, defeat at 0.
- **Honor**: Cannot Retreat after Turn 3.
