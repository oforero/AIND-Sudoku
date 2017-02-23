from collections import Counter
from typing import List, Set

from unit_builder import ValueResult
from unit_builder import Unit, Board, Constraint


def eliminate(sudoku, unit: Unit) -> ValueResult:
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


def only_choice(sudoku, unit: Unit) -> ValueResult:
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


def naked_twins(sudoku, unit: Unit) -> ValueResult:
    """Find pair of boxes with the same potential two values in a unit, and remove them of all other boxes in it"""
    def find_twins(unit: Unit) -> List[Set[chr]]:
        assigned = sudoku.get_assigned_values(unit)
        unit_values = map(lambda b: tuple(sorted(list(sudoku.board[b]))), unit)
        only_two = filter(lambda v: len(v) == 2, unit_values)
        counts = Counter(only_two)
        twins = [set(list(v)) for v, c in counts.items() if c > 1]
        twins = list(filter(lambda t: len(t) == 2, map(lambda t: t - assigned, twins)))
        return twins

    twins = find_twins(unit)
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