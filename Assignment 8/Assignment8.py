# we will use copy to make a deepcopy of the board
import copy
from typing import List, Any, Tuple

# import Stack and Queue classes for BFS/DFS
from stack_and_queue import Stack, Queue


def remove_if_exists(lst: Any, elem: Any) -> None:
    """Takes a list and element and removes that element if it exists in the list.

    Args:
        lst - the list you're trying to remove an item from
        elem - item to remove
    """
    if isinstance(lst, list) and elem in lst:
        lst.remove(elem)


class Board:
    """Represents a state (situation) in a Sudoku puzzle. Some cells may have filled in
    numbers while others have not. Cells that have not been filled in hold a list of
    the potential values that could be assigned to the cell (i.e. have not been ruled out
    from the row, column or subgrid)

    Attributes:
        num_nums_placed - number of numbers placed so far (initially 0)
        size - the size of the board (this will always be 9, but is convenient to have
            an attribute for this for debugging purposes)
        rows - a list of 9 lists, each with 9 elements (imagine a 9x9 sudoku board).
            Each element will itself be a list of the numbers that remain possible to
            assign in that square. Initially, each element will contain a list of the
            numbers 1 through 9 (so a triply nested 9x9x9 list to start) as all numbers
            are possible when no assignments have been made. When an assignment is made
            this innermost element won't be a list of possibilities anymore but the
            single number that is the assignment.
    """

    def __init__(self):
        """Constructor for a board, sets up a board with each element having all
        numbers as possibilities"""
        self.size: int = 9
        self.num_nums_placed: int = 0

        # triply nested lists, representing a 9x9 sudoku board
        # 9 quadrants, 9 cells in each 3*3 subgrid, 9 possible numbers in each cell
        # Note: using Any in the type hint since the cell can be either a list (when it
        # has not yet been assigned a value) or a number (once it has been assigned)
        self.rows: List[List[Any]] = []
        for i in range(self.size):
            arow = []
            for j in range(self.size):
                arow.append([1,2,3,4,5,6,7,8,9])
            self.rows.append(arow)

    def __str__(self) -> str:
        """String representation of the board"""
        row_str = ""
        for r in self.rows:
            row_str += f"{r}\n"

        return f"num_nums_placed: {self.num_nums_placed}\nboard (rows): \n{row_str}"

    def print_pretty(self):
        """Prints all numbers assigned to cells, excluding lists of possible numbers
        that can still be assigned to cells"""
        row_str = ""
        for i, r in enumerate(self.rows):
            if not i % 3:
                row_str += " -------------------------\n"

            for j, x in enumerate(r):
                row_str += " | " if not j % 3 else " "
                row_str += "*" if isinstance(x, list) else f"{x}"

            row_str += " |\n"

        row_str += " -------------------------\n"
        print(f"num_nums_placed: {self.num_nums_placed}\nboard (rows): \n{row_str}")

    def subgrid_coordinates(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all coordinates of cells in a given cell's subgrid (3x3 space)

        Integer divide to get column & row indices of subgrid then take all combinations
        of cell indices with the row/column indices from those subgrids (also known as
        the outer or Cartesian product)

        Args:
            row - index of the cell's row, 0 - 8
            col - index of the cell's col, 0 - 8

        Returns:
            list of (row, col) that represent all cells in the box.
        """
        # Note: row // 3 gives the index of the subgrid for the row index, this is one
        # of 0, 1 or 2, col // 3 gives us the same for the column
        coords = []
        for r in range(self.size):
            for c in range(self.size):
                if r//3 == row//3 and c//3 == col//3:
                    coords.append((r,c))
        return coords

    def find_most_constrained_cell(self) -> Tuple[int, int]:
        """Finds the coordinates (row and column indices) of the cell that contains the
        fewest possible values to assign (the shortest list). Note: in the case of ties
        return the coordinates of the first minimum size cell found

        Returns:
            a tuple of row, column index identifying the most constrained cell
        """
        shortest_cell_size = 9 #max is 9 numbers possible
        shortest_cell_coords = None
        for r in range(self.size):
            for c in range(self.size):
                if isinstance(self.rows[r][c], list) and len(self.rows[r][c]) < shortest_cell_size: #check if the cell is a list
                    shortest_cell_size = len(self.rows[r][c])
                    shortest_cell_coords = (r, c)

                    #special case, if the cell only has one possible number, we return it immediately (there can be nothing shorter)
                    #this doesn't change the big O, just an optimization
                    if shortest_cell_size == 1:
                        return shortest_cell_coords
        #return the coordinates of the shortest cell
        return shortest_cell_coords

        return None

    def failure_test(self) -> bool:
        """Check if we've failed to correctly fill out the puzzle. If we find a cell
        that contains an [], then we have no more possibilities for the cell but haven't
        assigned it a value so fail.

        Returns:
            True if we have failed to fill out the puzzle, False otherwise
        """
        #we check if any cell contains an empty list, if so, we have failed
        for row in self.rows:
            for cell in row:
                if cell == []:
                    return True
        return False


    def goal_test(self) -> bool:
        """Check if we've completed the puzzle (if we've placed all the numbers).
        Naively checks that we've placed as many numbers as cells on the board

        Returns:
            True if we've placed all numbers, False otherwise
        """
        #for a standard 9x9 sudoku board, we have 81 cells, so we check if we have placed all 81 numbers
        return self.num_nums_placed == self.size * self.size
    
    def update(self, row: int, column: int, assignment: int) -> None:
        """Assigns the given value to the cell given by passed in row and column
        coordinates. By assigning we mean set the cell to the value so instead the cell
        being a list of possibities it's just the new assignment value.  Update all
        affected cells (row, column & subgrid) to remove the possibility of assigning
        the given value.

        Args:
            row - index of the row to assign
            column - index of the column to assign
            assignment - value to place at given row, column coordinate
        """
        #we update the cell at the given row and column to the given assignment
        self.rows[row][column] = assignment
        #update the potential on the rest of the board
        #update the potential in the row
        for i in range(len(self.rows)):
            remove_if_exists(self.rows[i][column], assignment)

        #update the potential in the column
        for j in range(self.size):
            remove_if_exists(self.rows[row][j], assignment)

        #update the potential in the subgrid
        subgrid_coords = self.subgrid_coordinates(row, column)
        for coord in subgrid_coords:
            remove_if_exists(self.rows[coord[0]][coord[1]], assignment)

        #increment the number of numbers placed
        self.num_nums_placed += 1

def generic_search(state:Board, container:Stack or Queue) -> Board:
    """Performs a generic search. Takes a Board and a container (stack or queue) and attempts to assign values to most constrained cells until a solution is reached or a mistake has been made at which point it backtracks.
    Args:
        state - an instance of the Board class to solve, need to find most constrained cell and attempt an assignment
        container - a stack or queue to store the states
    Returns:
        either None in the case of invalid input
        returns the solved board if we win
    """
    #Then, push the initial state onto the stack
    container.push(state)
    #for each state on the stack, pop it off, check if we have won
    while not container.is_empty():
        current_state = container.pop()
        #we test win or fail when we add the state to the stack, so no need to do it here
        most_constrained_cell = current_state.find_most_constrained_cell() #a tuple
        #add states of all possible moves
        for number in current_state.rows[most_constrained_cell[0]][most_constrained_cell[1]]:
            new_state = copy.deepcopy(current_state)
            #optimization - check if we have been here before with this number, if so, skip it
            new_state.update(most_constrained_cell[0], most_constrained_cell[1], number)
            #check if it's a failure, if so, skip it
            #check if it's a win, if so, return it
            if new_state.goal_test():
                state = new_state
                print("we won!")
                return state

            if new_state.failure_test():
                continue
            else:
                #push the new state onto the stack
                container.push(new_state)
    
    #if container is empty without us winning, return None - we have no solution
    return None


def DFS(state: Board) -> Board:
    """Performs a depth first search. Takes a Board and attempts to assign values to
    most constrained cells until a solution is reached or a mistake has been made at
    which point it backtracks.

    Args:
        state - an instance of the Board class to solve, need to find most constrained
            cell and attempt an assignment

    Returns:
        either None in the case of invalid input
        returns the solved board if we win
    """

    return generic_search(state, Stack())

def BFS(state: Board) -> Board:
    """Performs a breadth first search. Takes a Board and attempts to assign
    values to most constrained cells until a solution is reached or a mistake
    has been made at which point it backtracks.

    Args:
        state - an instance of the Board class to solve, need to find most
        constrained cell and attempt an assignment

    Returns:
        either None in the case of invalid input or a solved board
    """
    return generic_search(state, Stack())

#setting up a sudoku puzzle for testing
first_puzzle = [
    (0, 1, 7),
    (0, 7, 1),
    (1, 2, 9),
    (1, 3, 7),
    (1, 5, 4),
    (1, 6, 2),
    (2, 2, 8),
    (2, 3, 9),
    (2, 6, 3),
    (3, 1, 4),
    (3, 2, 3),
    (3, 4, 6),
    (4, 1, 9),
    (4, 3, 1),
    (4, 5, 8),
    (4, 7, 7),
    (5, 4, 2),
    (5, 6, 1),
    (5, 7, 5),
    (6, 2, 4),
    (6, 5, 5),
    (6, 6, 7),
    (7, 2, 7),
    (7, 3, 4),
    (7, 5, 1),
    (7, 6, 9),
    (8, 1, 3),
    (8, 7, 8),
]

#setting up a sudoku puzzle for testing
second_puzzle = [
    (0, 1, 2),
    (0, 3, 3),
    (0, 5, 5),
    (0, 7, 4),
    (1, 6, 9),
    (2, 1, 7),
    (2, 4, 4),
    (2, 7, 8),
    (3, 0, 1),
    (3, 2, 7),
    (3, 5, 9),
    (3, 8, 2),
    (4, 1, 9),
    (4, 4, 3),
    (4, 7, 6),
    (5, 0, 6),
    (5, 3, 7),
    (5, 6, 5),
    (5, 8, 8),
    (6, 1, 1),
    (6, 4, 9),
    (6, 7, 2),
    (7, 2, 6),
    (8, 1, 4),
    (8, 3, 8),
    (8, 5, 7),
    (8, 7, 5),
]

def driver_test_dfs_or_bfs(use_dfs: bool, moves: List[Tuple[int, int, int]]) -> None:
    b = Board()
    # make initial moves to set up board
    for move in moves:
        b.update(*move)

    # print initial board
    print("<<<<< Initial Board >>>>>\n")
    b.print_pretty()
    # solve board
    solution = (DFS if use_dfs else BFS)(b)
    # print solved board
    print("<<<<< Solved Board >>>>>\n")
    solution.print_pretty()
    return solution


if __name__ == "__main__":
    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    assert myb.find_most_constrained_cell() == (1,8), "find most constrained test 1"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    assert myb.find_most_constrained_cell() == (6,5), "find most constrained test 2"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    assert myb.find_most_constrained_cell() == (6,5), "find most constrained test 3"
    print("find most constrained test suite passed")
    

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    assert myb.failure_test() == False, "failure test test 1"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.rows[6][5] = []
    assert myb.failure_test() == True, "failure test test 2"
    print("failure test test suite passed")

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.rows[6][5] = []
    assert myb.goal_test() == False, "goal test test 1"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 81
    assert myb.goal_test() == True, "goal test test 2"
    print("goal test test suite passed")

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 1
    myb.update(0, 0, 3)
    assert myb.rows[0][0] == 3, "update test 1"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 1
    myb.update(0, 0, 3)
    assert myb.num_nums_placed == 2, "update test 2"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 1
    myb.update(0, 0, 3)
    assert 3 not in myb.rows[0][8], "update test 3"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 1
    myb.update(0, 0, 3)
    assert 3 not in myb.rows[5][0], "update test 4"

    myb = Board()
    myb.rows[7][5] = [2,4,6,7]
    myb.rows[1][8] = [4,6,7]
    myb.rows[3][5] = [1,3,4,5]
    myb.rows[8][7] = [1,2,3,4,5]
    myb.rows[6][5] = [2,3]
    myb.rows[4][3] = 5
    myb.num_nums_placed = 1
    myb.update(0, 0, 3)
    assert 3 not in myb.rows[2][2], "update test 5"
    print("update test suite passed")

    print("all function test suites passed")

    assert isinstance(driver_test_dfs_or_bfs(True, first_puzzle), Board), "DFS test 1"

    assert isinstance(driver_test_dfs_or_bfs(True, second_puzzle), Board), "DFS test 2"

    assert isinstance(driver_test_dfs_or_bfs(False, first_puzzle), Board), "BFS test 1"

    assert isinstance(driver_test_dfs_or_bfs(False, second_puzzle), Board), "BFS test 2"






