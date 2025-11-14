"""
Sudoku Web Application - Flask Backend
Provides API endpoints for puzzle generation, validation, solving, and hints
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import random
import copy
from typing import List, Tuple, Optional
import sys
import os

# Import the existing solver
sys.path.append(os.path.join(os.path.dirname(__file__), 'Assignment 8'))
from Assignment8 import Board, DFS

app = Flask(__name__)
CORS(app)

# Difficulty settings: (num_cells_to_remove, name)
DIFFICULTY_LEVELS = {
    'easy': 30,      # Remove 30 cells (51 filled)
    'medium': 45,    # Remove 45 cells (36 filled)
    'hard': 55       # Remove 55 cells (26 filled)
}


class PuzzleGenerator:
    """Generates sudoku puzzles at various difficulty levels"""

    @staticmethod
    def generate_solved_board() -> Board:
        """Generate a complete, valid sudoku solution"""
        board = Board()

        # Fill diagonal 3x3 boxes first (they're independent)
        for box in range(3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for i in range(3):
                for j in range(3):
                    row = box * 3 + i
                    col = box * 3 + j
                    board.update(row, col, nums[idx])
                    idx += 1

        # Use solver to complete the rest
        solved = DFS(board)
        return solved if solved else PuzzleGenerator.generate_solved_board()

    @staticmethod
    def create_puzzle(difficulty: str = 'medium') -> Tuple[List[List[int]], List[List[int]]]:
        """
        Create a puzzle by removing cells from a solved board
        Returns: (puzzle, solution) as 2D lists
        """
        # Generate a complete solution
        solved_board = PuzzleGenerator.generate_solved_board()

        # Extract the solution as a 2D list
        solution = []
        for row in solved_board.rows:
            solution_row = []
            for cell in row:
                solution_row.append(cell if isinstance(cell, int) else 0)
            solution.append(solution_row)

        # Create puzzle by removing cells
        puzzle = [row[:] for row in solution]  # Deep copy
        cells_to_remove = DIFFICULTY_LEVELS.get(difficulty, 45)

        # Get all cell positions
        all_positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(all_positions)

        # Remove cells while ensuring puzzle remains solvable
        removed = 0
        for row, col in all_positions:
            if removed >= cells_to_remove:
                break

            # Temporarily remove the cell
            backup = puzzle[row][col]
            puzzle[row][col] = 0

            # Verify puzzle is still solvable
            test_board = Board()
            for r in range(9):
                for c in range(9):
                    if puzzle[r][c] != 0:
                        test_board.update(r, c, puzzle[r][c])

            # Check if solvable
            if DFS(copy.deepcopy(test_board)):
                removed += 1
            else:
                # Restore the cell if removal makes it unsolvable
                puzzle[row][col] = backup

        return puzzle, solution


# Store current game sessions (in production, use Redis or database)
game_sessions = {}


@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')


@app.route('/api/new-puzzle', methods=['POST'])
def new_puzzle():
    """
    Generate a new puzzle
    Request body: {"difficulty": "easy|medium|hard"}
    """
    data = request.json
    difficulty = data.get('difficulty', 'medium')

    if difficulty not in DIFFICULTY_LEVELS:
        return jsonify({'error': 'Invalid difficulty level'}), 400

    puzzle, solution = PuzzleGenerator.create_puzzle(difficulty)

    # Generate session ID
    session_id = str(random.randint(100000, 999999))

    # Store session
    game_sessions[session_id] = {
        'puzzle': puzzle,
        'solution': solution,
        'initial_puzzle': [row[:] for row in puzzle]
    }

    return jsonify({
        'session_id': session_id,
        'puzzle': puzzle,
        'difficulty': difficulty
    })


@app.route('/api/validate-move', methods=['POST'])
def validate_move():
    """
    Validate if a move makes the board unsolvable
    Request: {"session_id": str, "row": int, "col": int, "value": int, "current_board": 2D list}
    """
    data = request.json
    session_id = data.get('session_id')
    row = data.get('row')
    col = data.get('col')
    value = data.get('value')
    current_board = data.get('current_board')

    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400

    session = game_sessions[session_id]
    solution = session['solution']

    # Check if it matches the solution
    is_correct = solution[row][col] == value

    # Check for basic rule violations (duplicate in row/col/box)
    has_conflict = False

    # Check row
    for c in range(9):
        if c != col and current_board[row][c] == value:
            has_conflict = True
            break

    # Check column
    if not has_conflict:
        for r in range(9):
            if r != row and current_board[r][col] == value:
                has_conflict = True
                break

    # Check 3x3 box
    if not has_conflict:
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and current_board[r][c] == value:
                    has_conflict = True
                    break
            if has_conflict:
                break

    # If there's a conflict, it's definitely wrong
    if has_conflict:
        return jsonify({
            'valid': False,
            'correct': False,
            'reason': 'conflict',
            'message': 'This number conflicts with existing numbers!'
        })

    # Check if this move makes the puzzle unsolvable
    test_board = Board()
    for r in range(9):
        for c in range(9):
            if current_board[r][c] != 0:
                if (r, c) == (row, col):
                    test_board.update(r, c, value)
                else:
                    test_board.update(r, c, current_board[r][c])

    is_solvable = DFS(copy.deepcopy(test_board)) is not None

    if not is_solvable:
        return jsonify({
            'valid': False,
            'correct': is_correct,
            'reason': 'unsolvable',
            'message': 'This move makes the puzzle unsolvable!'
        })

    return jsonify({
        'valid': True,
        'correct': is_correct,
        'reason': 'valid'
    })


@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    """
    Solve the current puzzle
    Request: {"session_id": str}
    """
    data = request.json
    session_id = data.get('session_id')

    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400

    solution = game_sessions[session_id]['solution']

    return jsonify({
        'solution': solution
    })


@app.route('/api/hint', methods=['POST'])
def get_hint():
    """
    Get a hint (reveal one correct cell)
    Request: {"session_id": str, "current_board": 2D list}
    """
    data = request.json
    session_id = data.get('session_id')
    current_board = data.get('current_board')

    if session_id not in game_sessions:
        return jsonify({'error': 'Invalid session'}), 400

    solution = game_sessions[session_id]['solution']
    initial_puzzle = game_sessions[session_id]['initial_puzzle']

    # Find all empty cells that aren't part of the initial puzzle
    empty_cells = []
    for r in range(9):
        for c in range(9):
            if current_board[r][c] == 0 and initial_puzzle[r][c] == 0:
                empty_cells.append((r, c))

    if not empty_cells:
        return jsonify({'error': 'No empty cells to hint'}), 400

    # Pick a random empty cell
    hint_row, hint_col = random.choice(empty_cells)
    hint_value = solution[hint_row][hint_col]

    return jsonify({
        'row': hint_row,
        'col': hint_col,
        'value': hint_value
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
