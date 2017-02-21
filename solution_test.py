import solution
import unittest

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print


ALL_UNITS = list(map(lambda unit: list(map(lambda box: box[0] + box[1], unit)), solution.ALL_UNITS))

def sudoku_is_solved(sudoku) -> bool:
    expected = '123456789'

    def is_unit_valid(unit) -> bool:
        values = "".join(sorted(map(lambda box: sudoku[box], unit)))
        print(values)
        return values == expected

    unit_checks = map(is_unit_valid, ALL_UNITS)
    #all_true = all(unit_checks)
    #print("Results: ", all_true, list(unit_checks))
    return all(unit_checks)




class TestDiagonalSudoku(unittest.TestCase):
    diagonal_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solved_diag_sudoku = {'G7': '8', 'G6': '9', 'G5': '7', 'G4': '3', 'G3': '2', 'G2': '4', 'G1': '6', 'G9': '5',
                          'G8': '1', 'C9': '6', 'C8': '7', 'C3': '1', 'C2': '9', 'C1': '1', 'C7': '5', 'C6': '3',
                          'C5': '2', 'C4': '8', 'E5': '9', 'E4': '1', 'F1': '5', 'F2': '2', 'F3': '9', 'F4': '6',
                          'F5': '3', 'F6': '7', 'F7': '4', 'F8': '1', 'F9': '8', 'B4': '7', 'B5': '1', 'B6': '6',
                          'B7': '2', 'B1': '8', 'B2': '5', 'B3': '3', 'B8': '4', 'B9': '9', 'I9': '3', 'I8': '2',
                          'I1': '7', 'I3': '8', 'I2': '1', 'I5': '6', 'I4': '5', 'I7': '9', 'I6': '4', 'A1': '2',
                          'A3': '7', 'A2': '6', 'E9': '7', 'A4': '9', 'A7': '3', 'A6': '5', 'A9': '1', 'A8': '8',
                          'E7': '6', 'E6': '2', 'E1': '3', 'E3': '4', 'E2': '8', 'E8': '5', 'A5': '4', 'H8': '6',
                          'H9': '4', 'H2': '3', 'H3': '5', 'H1': '9', 'H6': '1', 'H7': '7', 'H4': '2', 'H5': '8',
                          'D8': '9', 'D9': '2', 'D6': '8', 'D7': '3', 'D4': '4', 'D5': '5', 'D2': '7', 'D3': '6',
                          'D1': '5'}

    def test_solve(self):
        solved = sudoku_is_solved(solution.solve(self.diagonal_grid))
        print("WTF ", solved)
        self.assertEqual(True, solved)
        #self.assertEqual(solution.solve(self.diagonal_grid), self.solved_diag_sudoku)

if __name__ == '__main__':
    #tests = TestNakedTwins()
    #tests.test_naked_twins()
    unittest.main()
