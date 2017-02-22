from typing import Callable, Dict, List, Set, Tuple, Union, Optional
from itertools import chain, groupby
from collections import Counter
from enum import Enum

# Type Declarations
RowCol = Tuple[chr, chr, chr, chr, chr, chr, chr, chr, chr]
Box = Tuple[chr, chr]
Unit = Tuple[Box, Box, Box,
             Box, Box, Box,
             Box, Box, Box]

Values = Set[chr]
Board = Dict[Box, Values]

Constraint = Callable[[any, Unit], Board]

# Constants
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


class ValueResult(Enum):
    ERROR = 1
    UNCHANGED = 2
    OK = 3


class Sudoku(object):
    def __init__(self, grid: Union[str, Board], assignments=[], units=ALL_UNITS):
        self.__UNITS__ = units
        if isinstance(grid, str):
            flat_board = zip(ALL_BOXES, grid)
            self.board: Board = dict(map(lambda x: (x[0], set(chr(ord(x[1]))) if x[1] != '.' else BOX_VALUES),
                                         flat_board))
            self.assignments = []
            self.__UNITS__ = units

        else:
            self.board = grid
            self.assignments = assignments[::]
            self.__UNITS__ = units

    def __str__(self):
        return "".join(map(lambda it: '*' if len(it[1]) == 0 else
                                      list(it[1])[0] if len(it[1]) == 1 else '.',
                           sorted(self.board.items())))

    def copy(self):
        return Sudoku(self.board.copy(), self.assignments, self.__UNITS__)

    def is_solved(self) -> bool:
        return all(map(lambda it: len(it[1]) == 1, self.board.items())) and self.is_viable()

    def is_valid(self) -> bool:
        def is_unit_valid(unit) -> bool:
            values = set.union(*map(lambda box: self.board[box], unit))
            return values == BOX_VALUES

        unit_checks = map(is_unit_valid, self.__UNITS__)
        return all(unit_checks)

    def is_viable(self) -> bool:
        """Returns True if the board can still be solved"""
        def is_unit_viable(unit) -> bool:
            empty = [self.board[box] for box in unit if len(self.board[box]) == 0]
            if empty:
                return False
            values = chain(*[list(self.board[box]) for box in unit if len(self.board[box]) == 1])
            counts = Counter(values)
            repeated = list(map(lambda x: x > 1, counts.values()))
            return not any(repeated)

        unit_checks = list(map(is_unit_viable, self.__UNITS__))
        return all(unit_checks)

    def is_not_solved(self) -> bool:
        return not self.is_solved()

    def is_unsolvable(self) -> bool:
        return any(map(lambda it: len(it[1]) == 0, self.board.items()))

    def is_solvable(self) -> bool:
        return not self.is_unsolvable()

    def get_box_value(self, ix: Box) -> Values:
        return self.board[ix]

    def get_assigned_values(self, unit: Unit) -> Set[chr]:
        values = [self.board[box] for box in unit if len(self.board[box]) == 1]
        return set.union(*values) if values else set()

    def get_unassigned_values(self, unit: Unit) -> List[chr]:
        return list(chain(*[self.board[box] for box in unit if len(self.board[box]) > 1]))

    def get_units_for_box(self, box: Box) -> List[Unit]:
        return list(filter(lambda unit: box in unit, self.__UNITS__))

    def set_box_value(self, box: Box, v: Values) -> ValueResult:
        if not v or len(self.board[box]) == 1:
            return ValueResult.ERROR

        if self.board[box] == v:
            return ValueResult.UNCHANGED

        self.board[box] = v
        if len(v) == 1:
            self.assignments.append(convert_board(self.board, reverse=True))

        return ValueResult.OK

    def apply_constraint(self, constraints: List[Constraint]):
        stalled_board = False
        while not stalled_board:
            stalled_board = True
            for unit in self.__UNITS__:
                changed = False
                stalled = False
                while not stalled:
                    results = [constraint(self, unit) for constraint in constraints]
                    if ValueResult.ERROR in results:
                        return ValueResult.ERROR
                    changed = changed or ValueResult.OK in results
                    stalled = all(map(lambda r: r == ValueResult.UNCHANGED, results))
                stalled_board &= not changed

        return changed

    def box_with_fewer_values(self) -> Optional[Box]:
        boxes = list(filter(lambda x: x[0] > 1, [(len(self.board[box]), box) for box in ALL_BOXES]))
        box = None
        if boxes:
            _, box = min(filter(lambda x: x[0] > 1, [(len(self.board[box]), box) for box in ALL_BOXES]))
        return box

    def display(self):
        """
        Display the values as a 2-D grid.
        Args:
        values(dict): The sudoku in dictionary form
        """
        width = 1 + max(len(self.board[s]) for s in ALL_BOXES)
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in ROWS:
            print(''.join("".join(sorted(self.board[(r, c)])).center(width) +
                          ('|' if c in '36' else '') for c in COLS))
            if r in 'CF':
                print(line)


def eliminate(sudoku: Sudoku, unit: Unit) -> ValueResult:
    """Find the assigned values in the unit and remove the values from the options of all
       unassigned boxes in that unit"""
    assigned = sudoku.get_assigned_values(unit)
    changed = False
    error = False
    for box in unit:
        if len(sudoku.get_box_value(box)) > 1:
            old_v = sudoku.get_box_value(box)
            store = sudoku.set_box_value(box, old_v - assigned)
            changed = changed or store == ValueResult.OK
            error = error or store == ValueResult.ERROR
    return ValueResult.ERROR if error else ValueResult.OK if changed else ValueResult.UNCHANGED


def only_choice(sudoku: Sudoku, unit: Unit) -> ValueResult:
    """Find the values that can be assigned to only one box in the unit and do it"""
    assigned = sudoku.get_assigned_values(unit)
    unassigned = sudoku.get_unassigned_values(unit)
    counts = Counter(unassigned)
    uniques = set([v for v, c in counts.items() if c == 1]) - assigned
    changed = False
    error = False
    if uniques:
        for box in unit:
            if len(sudoku.get_box_value(box)) > 1:
                old_v = sudoku.get_box_value(box)
                new_v = old_v & uniques
                store = sudoku.set_box_value(box, new_v if new_v else old_v)
                changed = changed or store == ValueResult.OK
                error = error or store == ValueResult.ERROR

    return ValueResult.ERROR if error else ValueResult.OK if changed else ValueResult.UNCHANGED


def naked_twins(sudoku: Board, unit: Unit) -> ValueResult:
    assigned = sudoku.get_assigned_values(unit)
    unit_values = map(lambda b: tuple(sorted(list(sudoku.board[b]))), unit)
    only_two = filter(lambda v: len(v) == 2, unit_values)
    counts = Counter(only_two)
    twins = [set(list(v)) for v, c in counts.items() if c > 1]
    twins = list(filter(lambda t: t, map(lambda t: t - assigned, twins)))
    changed = False
    error = False
    for twin in twins:
        for box in unit:
            old_v = sudoku.board[box]
            if len(old_v) > 2:
                new_v = old_v - twin
                store = sudoku.set_box_value(box, new_v if new_v else old_v)
                changed = changed or store == ValueResult.OK
                error = error or store == ValueResult.ERROR

    return ValueResult.OK if changed else ValueResult.UNCHANGED


CONSTRAINTS: List[Constraint] = [eliminate, only_choice, naked_twins]


def convert_board(grid, reverse=False) -> Board:
    if reverse:
        return dict(map(lambda it: (it[0][0] + it[0][1], "".join(sorted(list(it[1])))), grid.items()))
    else:
        return dict(map(lambda it: ((it[0][0], it[0][1]), set(list(it[1]))), grid.items()))


def search(game: Sudoku, depth=0) -> Optional[Sudoku]:
    while game.is_viable() and game.is_not_solved():
        game.apply_constraint(CONSTRAINTS)
        if not game or not game.is_viable():
            #print("BAD STRATEGY ", depth)
            #game.display()
            return None

        #print("Searching")
        box_to_change = game.box_with_fewer_values()
        if box_to_change:
            for value in game.get_box_value(box_to_change):
                new_game = game.copy()
                new_game.set_box_value(box_to_change, set(value))
                #print("Try Search: ", depth)
                solution_attempt = search(new_game, depth+1)
                if not solution_attempt or not solution_attempt.is_viable():
                    continue
                return solution_attempt

    return game if game and game.is_valid() else None


def solve(grid: str, use_diagonal=False) -> Optional[Sudoku]:
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        use_diagonal: If true it will enforce a diagonal sudoku
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    game = Sudoku(grid, units=ALL_UNITS if use_diagonal else NOT_DIAGONAL_UNITS)
    game = search(game)
    return game if game and game.is_solved() else None


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #diag_sudoku_grid = "1..92....524.1...........7..5...81.2.........4.27...9..6...........3.945....71..6"
    solution = solve(diag_sudoku_grid, use_diagonal=True)
    if solution.is_valid():
        print("Solved Sudoku: ")
        solution.display()
    else:
        print("Bad Sudoku: ")
        solution.display()

    try:
        from visualize import visualize_assignments
        visualize_assignments(solution.assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
