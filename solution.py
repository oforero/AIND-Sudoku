from collections import Counter
from itertools import chain
from typing import List, Set, Union, Optional

from unit_builder import Box, Unit, Values, Board, Constraint, ValueResult
from unit_builder import ROWS, COLS, BOX_VALUES, ALL_BOXES, NOT_DIAGONAL_UNITS, ALL_UNITS
from strategies import CONSTRAINTS


class Sudoku(object):
    def __init__(self, grid: Union[str, Board], assignments=[], units=ALL_UNITS):
        """Construct a Sudoku from a String or a Board (Dictionary)"""
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
        """Copy constructor necessary for search"""
        return Sudoku(self.board.copy(), self.assignments, self.__UNITS__)

    def is_solved(self) -> bool:
        """True if all boxes has been assigned and the sudoku constraint holds for all units"""
        return all(map(lambda it: len(it[1]) == 1, self.board.items())) and self.is_viable()

    def is_valid(self) -> bool:
        """Checks if the sudoku constraint holds for all units by checking the assigned boxes"""
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
        """True if a box has been assigned an empty value"""
        return any(map(lambda it: len(it[1]) == 0, self.board.items()))

    def is_solvable(self) -> bool:
        return not self.is_unsolvable()

    def get_box_value(self, ix: Box) -> Values:
        return self.board[ix]

    def get_assigned_values(self, unit: Unit) -> Set[chr]:
        """Returns a set of the values of assigned boxes for a given unit"""
        values = [self.board[box] for box in unit if len(self.board[box]) == 1]
        return set.union(*values) if values else set()

    def get_unassigned_values(self, unit: Unit) -> List[chr]:
        """Returns a list of all the values that remain to be assigned in the unit"""
        return list(chain(*[self.board[box] for box in unit if len(self.board[box]) > 1]))

    def get_units_for_box(self, box: Box) -> List[Unit]:
        """Returns the units to which the box belongs"""
        return list(filter(lambda unit: box in unit, self.__UNITS__))

    def set_box_value(self, box: Box, v: Values) -> ValueResult:
        """Sets the value of a box and return a Status:
              ERROR: If it tries to assign a box already assigned
              UNCHANGED: If the new and the old value are the same
              OK: In all the other cases
              """
        if not v or len(self.board[box]) == 1:
            return ValueResult.ERROR

        if self.board[box] == v:
            return ValueResult.UNCHANGED

        self.board[box] = v
        if len(v) == 1:
            self.assignments.append(convert_board(self.board, reverse=True))

        return ValueResult.OK

    def apply_constraint(self, constraints: List[Constraint]):
        """Repeatedly apply the strategies until no further simplification is possible"""
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
        """Find the unassigned box with the fewer number of possible values"""
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
