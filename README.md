# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?
A: I think this question is not clear.  Sudoku has only one real constraint which is that each unit must have no repeated digits.
I expressed it in the code in the method called eliminate.
Things like only choice or naked twins are more properly understood as strategies to reduce the size of the search space.
I implemented a general method in the Sudoku that executes one strategy through all the relevant units; following the classic Strategy Pattern but using Higher Order Functions to simplify its implementation. When building the Sudoku object one pass a list of the strategies to use to reach a solution.

# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?
A: I implemented a Sudoku approach that does not hard coded the Units.
The units are parameters at construction time; the units representation is a tuple of eight elements.
Adding the diagonal constraint is achieved by passing a collection containing the diagonal groups. The rest of the code remains the same, and the Sudoku constraint and solution strategies are applied to all the units used to construct the Sudoku object.

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solutions.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Data

The data consists of a text file of diagonal sudokus for you to solve.