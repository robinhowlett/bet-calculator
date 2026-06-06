# CLAUDE.md

## What This Is

bet-calculator is a pure mechanics library for pari-mutuel wagering. It knows:
- Every bet type (Win through Pick 6)
- How to construct tickets (straight, box, key, wheel, part-wheel, horizontal)
- How to count combinations and compute costs
- How to track which combinations are alive as legs resolve

It does NOT know:
- Probabilities (that's race-explanation)
- Expected value (that's wagering-analytics)
- When to bet or how much (that's race-day-sim)

## Setup

```bash
pip install -e ".[dev]"
pytest
```

No database, no dependencies beyond Python stdlib.

## Architecture

```
src/bet_calculator/
├── types.py    # BetType definitions (Win, Exacta, Pick 4, etc.)
└── ticket.py   # Ticket construction + combination tracking + resolution
```

## Conventions

- Program numbers are integers (1-indexed, matching the race program)
- Combinations are tuples of program numbers in order
- For verticals: order matters (5,6,7 ≠ 6,5,7 in a trifecta)
- For horizontals: each position is one leg's winner
- Unit cost is per-combination (total = n_combinations × unit)
