"""Bet types and their properties.

Defines every pari-mutuel bet type offered at US/Canadian tracks:
- Vertical (single-race): Win, Place, Show, Exacta, Trifecta, Superfecta, Hi-5
- Horizontal (multi-race): Daily Double, Pick 3, Pick 4, Pick 5, Pick 6

Each type knows: how many positions matter, minimum unit cost, how
combinations are counted, and whether it's vertical or horizontal.
"""
from dataclasses import dataclass
from enum import Enum


class BetCategory(Enum):
    WIN_PLACE_SHOW = "wps"
    VERTICAL_EXOTIC = "vertical"
    HORIZONTAL_EXOTIC = "horizontal"


@dataclass(frozen=True)
class BetType:
    name: str
    category: BetCategory
    positions: int          # how many finishing positions matter (exacta=2, tri=3, etc.)
    legs: int              # number of races (1 for verticals, N for horizontals)
    min_unit: float        # typical minimum bet unit ($2 for most, $0.50/$1 for supers)
    typical_takeout: float # rough national average takeout for this pool

    @property
    def is_vertical(self) -> bool:
        return self.legs == 1

    @property
    def is_horizontal(self) -> bool:
        return self.legs > 1


# Standard bet types
WIN = BetType("Win", BetCategory.WIN_PLACE_SHOW, positions=1, legs=1, min_unit=2.0, typical_takeout=0.16)
PLACE = BetType("Place", BetCategory.WIN_PLACE_SHOW, positions=2, legs=1, min_unit=2.0, typical_takeout=0.16)
SHOW = BetType("Show", BetCategory.WIN_PLACE_SHOW, positions=3, legs=1, min_unit=2.0, typical_takeout=0.16)

EXACTA = BetType("Exacta", BetCategory.VERTICAL_EXOTIC, positions=2, legs=1, min_unit=2.0, typical_takeout=0.20)
TRIFECTA = BetType("Trifecta", BetCategory.VERTICAL_EXOTIC, positions=3, legs=1, min_unit=1.0, typical_takeout=0.24)
SUPERFECTA = BetType("Superfecta", BetCategory.VERTICAL_EXOTIC, positions=4, legs=1, min_unit=0.50, typical_takeout=0.25)
HI_FIVE = BetType("Hi-5", BetCategory.VERTICAL_EXOTIC, positions=5, legs=1, min_unit=1.0, typical_takeout=0.25)

DAILY_DOUBLE = BetType("Daily Double", BetCategory.HORIZONTAL_EXOTIC, positions=1, legs=2, min_unit=2.0, typical_takeout=0.20)
PICK_3 = BetType("Pick 3", BetCategory.HORIZONTAL_EXOTIC, positions=1, legs=3, min_unit=1.0, typical_takeout=0.24)
PICK_4 = BetType("Pick 4", BetCategory.HORIZONTAL_EXOTIC, positions=1, legs=4, min_unit=1.0, typical_takeout=0.24)
PICK_5 = BetType("Pick 5", BetCategory.HORIZONTAL_EXOTIC, positions=1, legs=5, min_unit=1.0, typical_takeout=0.25)
PICK_6 = BetType("Pick 6", BetCategory.HORIZONTAL_EXOTIC, positions=1, legs=6, min_unit=2.0, typical_takeout=0.25)

ALL_BET_TYPES = [WIN, PLACE, SHOW, EXACTA, TRIFECTA, SUPERFECTA, HI_FIVE,
                 DAILY_DOUBLE, PICK_3, PICK_4, PICK_5, PICK_6]

BET_TYPE_BY_NAME = {bt.name: bt for bt in ALL_BET_TYPES}
