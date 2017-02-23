from itertools import groupby, chain
from typing import Tuple, Set, Dict, Callable, List
from enum import Enum


class ValueResult(Enum):
    ERROR = 1
    UNCHANGED = 2
    OK = 3

RowCol = Tuple[chr, chr, chr, chr, chr, chr, chr, chr, chr]
Box = Tuple[chr, chr]
Unit = Tuple[Box, Box, Box,
             Box, Box, Box,
             Box, Box, Box]
Values = Set[chr]
Board = Dict[Box, Values]
Constraint = Callable[[any, Unit], Board]
ROWS: RowCol = tuple(map(chr, range(ord('A'), ord('I')+1)))
COLS: RowCol = tuple(map(chr, range(ord('1'), ord('9')+1)))
BOX_VALUES: Values = set(COLS)
ALL_BOXES: List[Box] = [tuple([r, c]) for r in ROWS for c in COLS]
ROW_UNITS: List[Unit] = list(map(lambda g: tuple(g[1]), groupby(ALL_BOXES, lambda box: box[0])))
COL_UNITS: List[Unit] = list(map(lambda g: tuple(g[1]), groupby(sorted(ALL_BOXES, key=lambda b: b[1]),
                                                                lambda box: box[1])))


def box_unit(box: Box) -> int:
    return (1 if box[0] in ['A', 'B', 'C'] and box[1] in ['1', '2', '3'] else
            2 if box[0] in ['A', 'B', 'C'] and box[1] in ['4', '5', '6'] else
            3 if box[0] in ['A', 'B', 'C'] and box[1] in ['7', '8', '9'] else
            4 if box[0] in ['D', 'E', 'F'] and box[1] in ['1', '2', '3'] else
            5 if box[0] in ['D', 'E', 'F'] and box[1] in ['4', '5', '6'] else
            6 if box[0] in ['D', 'E', 'F'] and box[1] in ['7', '8', '9'] else
            7 if box[0] in ['G', 'H', 'I'] and box[1] in ['1', '2', '3'] else
            8 if box[0] in ['G', 'H', 'I'] and box[1] in ['4', '5', '6'] else
            9)


BOX_UNITS: List[Unit] = list(map(lambda g: tuple(g[1]), groupby(sorted(ALL_BOXES, key=box_unit),
                                                                box_unit)))


def diagonal_unit_1(box: Box) -> int:
    return "".join(box) in ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']


def diagonal_unit_2(box: Box) -> int:
    return "".join(box) in ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']


DIAGONAL_UNITS: List[Unit] = [tuple(filter(diagonal_unit_1, ALL_BOXES)),
                              tuple(filter(diagonal_unit_2, ALL_BOXES))]
NOT_DIAGONAL_UNITS: List[Unit] = list(chain(ROW_UNITS, COL_UNITS, BOX_UNITS))
ALL_UNITS: List[Unit] = list(chain(NOT_DIAGONAL_UNITS, DIAGONAL_UNITS))


def build_unit(ix: chr, other: RowCol, ix_first=True) -> Unit:
    if ix_first:
        return tuple(map(lambda o: Box(ix, o), other))
    else:
        return tuple(map(lambda o: Box(o, ix), other))