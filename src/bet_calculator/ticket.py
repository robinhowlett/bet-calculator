"""Ticket construction and combination enumeration.

A Ticket represents a specific wagering action: bet type + selections + unit cost.
It knows how to enumerate all individual combinations it covers, compute total cost,
and track which combinations are still alive as results are revealed.

Construction methods:
- Straight: specific exact order (5-6-7 trifecta)
- Box: all permutations of selected horses (box 5,6,7 = 6 trifecta combos)
- Key: one horse fixed in a position, others fill remaining (key 5 with 2,3,6,7)
- Key-box: one horse on top, box the rest underneath
- Wheel: one horse in one position, ALL others in remaining positions
- Part-wheel: specific horses in specific positions (most flexible)
"""
from dataclasses import dataclass, field
from itertools import permutations, product
from .types import BetType, EXACTA, TRIFECTA, SUPERFECTA, DAILY_DOUBLE, PICK_3, PICK_4, PICK_5, PICK_6


@dataclass
class Combination:
    """One specific combination within a ticket.

    For verticals: selections is a tuple of program numbers in finish order.
    For horizontals: selections is a tuple of program numbers, one per leg.
    """
    selections: tuple       # e.g. (5, 6, 7) for a 5-6-7 trifecta
    alive: bool = True      # still valid (not eliminated by a revealed result)

    def __hash__(self):
        return hash(self.selections)

    def __eq__(self, other):
        return self.selections == other.selections


@dataclass
class Ticket:
    """A wagering ticket — a bet type + selections + unit cost.

    Knows all its individual combinations and can track which are alive.
    """
    bet_type: BetType
    combinations: list[Combination]
    unit_cost: float
    description: str = ""   # human-readable: "Key 5 with 2,3,6,7 Trifecta"

    @property
    def n_combinations(self) -> int:
        return len(self.combinations)

    @property
    def total_cost(self) -> float:
        return self.n_combinations * self.unit_cost

    @property
    def alive_combinations(self) -> list[Combination]:
        return [c for c in self.combinations if c.alive]

    @property
    def n_alive(self) -> int:
        return len(self.alive_combinations)

    @property
    def is_alive(self) -> bool:
        return self.n_alive > 0

    def resolve_leg(self, leg_index: int, winner: int):
        """Mark combinations dead if they don't have the winner in the specified leg.

        For horizontals: leg_index is which leg just resolved (0-indexed).
        For verticals: leg_index is which position just became known.
        """
        for combo in self.combinations:
            if combo.alive and combo.selections[leg_index] != winner:
                combo.alive = False

    def resolve_vertical(self, result: tuple):
        """Resolve a vertical bet against the full finishing order.

        result: tuple of program numbers in actual finish order.
        Only the combination matching the result (in order) survives.
        """
        for combo in self.combinations:
            if combo.alive and combo.selections != result[:len(combo.selections)]:
                combo.alive = False

    def is_winner(self, result: tuple) -> bool:
        """Check if this ticket hits given the result."""
        target = result[:self.bet_type.positions]
        return any(c.selections == target for c in self.combinations)


# ============================================================
# Construction methods
# ============================================================

def straight(bet_type: BetType, selections: tuple, unit: float = None) -> Ticket:
    """Single specific combination. E.g. 5-6-7 trifecta."""
    unit = unit or bet_type.min_unit
    combo = Combination(selections=selections)
    desc = "-".join(str(s) for s in selections)
    return Ticket(bet_type=bet_type, combinations=[combo], unit_cost=unit,
                  description=f"{desc} {bet_type.name}")


def box(bet_type: BetType, runners: list[int], unit: float = None) -> Ticket:
    """All permutations of the selected runners.

    E.g. box(TRIFECTA, [5,6,7]) = 6 combinations (all orderings of 5,6,7).
    """
    unit = unit or bet_type.min_unit
    n_positions = bet_type.positions
    combos = [Combination(selections=perm)
              for perm in permutations(runners, n_positions)]
    desc = f"Box {','.join(str(r) for r in runners)} {bet_type.name}"
    return Ticket(bet_type=bet_type, combinations=combos, unit_cost=unit,
                  description=desc)


def key(bet_type: BetType, key_runner: int, with_runners: list[int],
        position: int = 0, unit: float = None) -> Ticket:
    """One horse fixed in a position, others fill remaining positions.

    E.g. key(TRIFECTA, 5, [2,3,6,7], position=0) = 5 on top, permutations
    of 2,3,6,7 for 2nd and 3rd = 12 combinations.
    """
    unit = unit or bet_type.min_unit
    n_positions = bet_type.positions
    other_positions = n_positions - 1

    combos = []
    for perm in permutations(with_runners, other_positions):
        selections = list(perm)
        selections.insert(position, key_runner)
        combos.append(Combination(selections=tuple(selections)))

    with_str = ','.join(str(r) for r in with_runners)
    pos_label = {0: "on top", 1: "2nd", 2: "3rd", 3: "4th"}
    desc = f"Key {key_runner} {pos_label.get(position, '')} with {with_str} {bet_type.name}"
    return Ticket(bet_type=bet_type, combinations=combos, unit_cost=unit,
                  description=desc)


def key_box(bet_type: BetType, key_runner: int, with_runners: list[int],
            unit: float = None) -> Ticket:
    """Key horse on top, box the remaining positions.

    E.g. key_box(TRIFECTA, 5, [2,3,6,7]) = 5 always 1st, all permutations
    of 2,3,6,7 for 2nd/3rd = 12 combinations.
    Same as key(..., position=0) for trifecta.
    """
    return key(bet_type, key_runner, with_runners, position=0, unit=unit)


def wheel(bet_type: BetType, key_runner: int, field_size: int,
          position: int = 0, unit: float = None) -> Ticket:
    """Key horse in one position, ALL other runners fill remaining.

    E.g. wheel(EXACTA, 5, field_size=8, position=0) = 5 on top with all
    7 others underneath = 7 combinations.
    """
    all_others = [i for i in range(1, field_size + 1) if i != key_runner]
    return key(bet_type, key_runner, all_others, position=position, unit=unit)


def part_wheel(bet_type: BetType, positions: list[list[int]],
               unit: float = None) -> Ticket:
    """Specific horses in specific positions — most flexible construction.

    positions: list of lists, one per position. Each inner list is the
    runners eligible for that position.

    E.g. part_wheel(TRIFECTA, [[5], [2,3,6], [2,3,6,7,8]]) =
    5 on top, 2/3/6 in 2nd, 2/3/6/7/8 in 3rd (excluding duplicates).
    """
    unit = unit or bet_type.min_unit
    combos = []

    for combo_tuple in product(*positions):
        # Skip if any runner appears in multiple positions
        if len(set(combo_tuple)) == len(combo_tuple):
            combos.append(Combination(selections=combo_tuple))

    desc_parts = ['/'.join(str(r) for r in pos) for pos in positions]
    desc = f"{' with '.join(desc_parts)} {bet_type.name}"
    return Ticket(bet_type=bet_type, combinations=combos, unit_cost=unit,
                  description=desc)


def horizontal(bet_type: BetType, legs: list[list[int]],
               unit: float = None) -> Ticket:
    """Multi-race bet with selections per leg.

    legs: list of lists, one per race. Each inner list is the runners
    selected in that leg.

    E.g. horizontal(PICK_3, [[5,6], [2,3], [1,4,7]]) = 2×2×3 = 12 combos.
    """
    unit = unit or bet_type.min_unit
    assert len(legs) == bet_type.legs, f"{bet_type.name} requires {bet_type.legs} legs, got {len(legs)}"

    combos = [Combination(selections=combo)
              for combo in product(*legs)]

    leg_strs = ['/'.join(str(r) for r in leg) for leg in legs]
    desc = f"{bet_type.name}: {' × '.join(leg_strs)}"
    return Ticket(bet_type=bet_type, combinations=combos, unit_cost=unit,
                  description=desc)
