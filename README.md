# bet-calculator

Pure mechanics for pari-mutuel wagering: bet types, ticket construction, cost calculation, combination enumeration, and leg-by-leg resolution tracking.

No opinions, no probabilities, no database — just "here's what this ticket IS."

Consumed by [race-day-sim](https://github.com/robinhowlett/race-day-sim) (via `tickets.py`) to construct bets from classified opinions.

## What it does

```python
from bet_calculator.types import TRIFECTA, PICK_4
from bet_calculator.ticket import key, horizontal, box

# Key 5 on top with 2,3,6,7 in a $1 trifecta
ticket = key(TRIFECTA, key_runner=5, with_runners=[2, 3, 6, 7], unit=1.0)
ticket.n_combinations  # 12
ticket.total_cost      # $12.00
ticket.is_winner((5, 6, 7, 1))  # True (5-6-7 is one of the 12 combos)

# Pick 4: single-spread-spread-single
ticket = horizontal(PICK_4, legs=[[5], [2, 3], [1, 4, 7], [6]], unit=1.0)
ticket.n_combinations  # 6
ticket.total_cost      # $6.00

# Resolve leg by leg
ticket.resolve_leg(0, winner=5)  # Leg 1: #5 wins — still alive
ticket.resolve_leg(1, winner=3)  # Leg 2: #3 wins — 3 combos alive
ticket.resolve_leg(2, winner=4)  # Leg 3: #4 wins — 1 combo alive
ticket.resolve_leg(3, winner=6)  # Leg 4: #6 wins — HIT!
```

## Construction methods

| Method | What it does | Example |
|--------|-------------|---------|
| `straight(type, (5,6,7))` | One specific combination | 5-6-7 trifecta, 1 combo |
| `box(type, [5,6,7])` | All permutations | Box 5,6,7 trifecta, 6 combos |
| `key(type, 5, [2,3,6,7])` | One horse fixed, others fill | Key 5 with 2,3,6,7 tri, 12 combos |
| `key_box(type, 5, [2,3,6,7])` | Key on top, box underneath | Same as key position=0 |
| `wheel(type, 5, field=8)` | Key with ALL others | 5 with field exacta, 7 combos |
| `part_wheel(type, [[5],[2,3,6],[2,3,6,7,8]])` | Specific per position | Most flexible |
| `horizontal(type, [[5],[2,3],[1,4,7],[6]])` | Multi-race selections per leg | Pick 4, 6 combos |

## Bet types

| Type | Positions | Legs | Min unit |
|------|---:|---:|---:|
| Win / Place / Show | 1/2/3 | 1 | $2 |
| Exacta | 2 | 1 | $2 |
| Trifecta | 3 | 1 | $1 |
| Superfecta | 4 | 1 | $0.50 |
| Hi-5 | 5 | 1 | $1 |
| Daily Double | 1 | 2 | $2 |
| Pick 3 | 1 | 3 | $1 |
| Pick 4 | 1 | 4 | $1 |
| Pick 5 | 1 | 5 | $1 |
| Pick 6 | 1 | 6 | $2 |

## Resolution

For vertical bets: `ticket.resolve_vertical((5, 6, 7, 1))` — marks all non-matching combos dead.

For horizontal bets: `ticket.resolve_leg(leg_index, winner)` — call after each leg. Track `ticket.n_alive` to see how many combinations survive.
