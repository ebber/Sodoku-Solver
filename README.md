# Sudoku Web Application

A fully-featured, interactive Sudoku game built with Flask backend and vanilla JavaScript frontend. Features include multiple difficulty levels, lives system, timer, scoring, hints, pencil marks, undo/redo, and switchable light/dark themes.

## Features

### Core Gameplay
- **Interactive Sudoku Board**: Click cells and input numbers with on-screen number pad or keyboard
- **3 Difficulty Levels**: Easy, Medium, and Hard puzzles with varying complexity
- **Lives System**: Start with 3 lives; lose one for each move that makes the puzzle unsolvable
- **Real-time Validation**: Immediate feedback on whether moves are valid or make puzzle unsolvable
- **Auto-Solve**: Button to instantly reveal the complete solution

### Enhanced Features
- **Timer & Scoring**: Track solving time and earn points based on performance
- **Hint System**: Get hints that reveal correct numbers (with score penalty)
- **Pencil Marks**: Add small candidate numbers to cells for note-taking
- **Undo/Redo**: Full history navigation with keyboard shortcuts (Ctrl/Cmd+Z)
- **Keyboard Navigation**: Arrow keys to move, numbers to fill, Delete to erase
- **Theme Switcher**: Toggle between beautiful Light and Dark themes
- **Conflict Highlighting**: Visual feedback for invalid moves
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Python Flask with CORS support
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Solver**: Backtracking algorithm with constraint propagation
- **Puzzle Generation**: Smart removal algorithm ensuring unique solutions

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the repository**
   ```bash
   cd "Sodoku-Solver"
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode (Local Testing)

1. **Activate the virtual environment** (if not already activated)
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Start the Flask development server**
   ```bash
   python app.py
   ```

3. **Open your browser**
   Navigate to: `http://localhost:5000`

### Production Mode (Deployment)

For production deployment with better performance and stability:

1. **Make run script executable** (first time only)
   ```bash
   chmod +x run.sh
   ```

2. **Run the production server**
   ```bash
   ./run.sh
   ```

   This will:
   - Set up the virtual environment
   - Install all dependencies
   - Stop any existing instances
   - Start gunicorn with 4 worker processes
   - Serve the app on `http://0.0.0.0:8000`

3. **Access the application**
   - Local: `http://localhost:8000`
   - Network: `http://YOUR_IP:8000`

### Cloud Deployment (Heroku)

This app is ready for Heroku deployment:

```bash
# Install Heroku CLI and login
heroku login

# Create a new Heroku app
heroku create your-sudoku-app

# Deploy
git push heroku main

# Open the app
heroku open
```

### Playing the Game

1. **Start playing!**
   - Select a difficulty level
   - Click cells to select them
   - Use the number pad or keyboard (1-9) to fill in numbers
   - Try to complete the puzzle without losing all 3 lives!

2. **Important:** Invalid moves that would make the puzzle unsolvable will:
   - Flash red
   - Cost you a life
   - Be automatically reverted (board stays solvable)

## How to Play

### Basic Controls

**Mouse/Touch:**
- Click/tap a cell to select it
- Click number pad buttons to enter numbers
- Use control buttons for special actions

**Keyboard:**
- **Arrow Keys**: Navigate between cells
- **1-9**: Enter numbers in selected cell
- **Delete/Backspace**: Erase selected cell
- **P**: Toggle pencil mode
- **Ctrl/Cmd+Z**: Undo last move
- **Ctrl/Cmd+Shift+Z**: Redo move

### Game Mechanics

1. **Lives**: You start with 3 lives (❤️❤️❤️)
   - Lose a life when a move makes the puzzle unsolvable
   - Game over when all lives are lost

2. **Scoring**:
   - +10 points for each correct number
   - -15 points for each lost life
   - -20 points for each hint used
   - Time bonus for fast completion
   - Lives bonus at game end

3. **Pencil Marks**:
   - Enable with the "✏️ Pencil Mode" button
   - Add small candidate numbers to cells
   - Automatically cleared when you enter a final number

4. **Hints**:
   - Click "💡 Hint" to reveal one correct number
   - Score penalty applied for each hint
   - Strategically use hints when stuck

5. **Win Condition**:
   - Fill all 81 cells correctly
   - View your final score and stats

## Project Structure

```
Sodoku-Solver/
├── app.py                      # Flask backend server
├── requirements.txt            # Python dependencies
├── Assignment 8/
│   ├── Assignment8.py          # Core sudoku solver logic
│   └── stack_and_queue.py      # Data structures
├── templates/
│   └── index.html              # Main game page
├── static/
│   ├── css/
│   │   └── styles.css          # Styles with theme system
│   └── js/
│       └── game.js             # Game logic and UI
└── venv/                       # Virtual environment (not in git)
```

## API Endpoints

The Flask backend provides the following REST API endpoints:

- `GET /` - Serve the main game page
- `POST /api/new-puzzle` - Generate a new puzzle
  - Body: `{"difficulty": "easy|medium|hard"}`
  - Returns: `{"session_id": str, "puzzle": 2D array, "difficulty": str}`

- `POST /api/validate-move` - Validate a player's move
  - Body: `{"session_id": str, "row": int, "col": int, "value": int, "current_board": 2D array}`
  - Returns: `{"valid": bool, "correct": bool, "reason": str, "message": str}`

- `POST /api/solve` - Get the complete solution
  - Body: `{"session_id": str}`
  - Returns: `{"solution": 2D array}`

- `POST /api/hint` - Get a hint (reveal one cell)
  - Body: `{"session_id": str, "current_board": 2D array}`
  - Returns: `{"row": int, "col": int, "value": int}`

## Algorithm Details

### Solver Algorithm
The solver uses a **backtracking algorithm with constraint propagation**:
1. Find the most constrained cell (fewest possible values)
2. Try each possible value for that cell
3. Propagate constraints (remove value from row/col/box)
4. Recursively solve the remaining puzzle
5. Backtrack if a dead-end is reached

This approach is efficient and guarantees finding a solution if one exists.

### Puzzle Generation
1. Generate a complete solved board by filling diagonal boxes randomly
2. Use the solver to complete the rest of the board
3. Remove cells based on difficulty:
   - Easy: ~30 cells removed (~51 given)
   - Medium: ~45 cells removed (~36 given)
   - Hard: ~55 cells removed (~26 given)
4. Verify each removal still leaves a solvable puzzle

## Development

### Adding Features
The codebase is structured for easy extension:
- **Backend**: Add new endpoints in `app.py`
- **Frontend Logic**: Extend the `SudokuGame` class in `game.js`
- **Styling**: Modify CSS variables in `styles.css` for theme customization

### Theme Customization
Both themes are defined using CSS variables in `styles.css`:
- Light theme: Clean, professional look
- Dark theme: Easy on the eyes for extended play

To add a new theme, copy the variable definitions and adjust colors.

## Troubleshooting

**"Module not found" errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Port 5000 already in use:**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`
- Update the URL in your browser accordingly

**Puzzle generation is slow:**
- Normal for hard puzzles (requires verification of solvability)
- Consider reducing the number of cells removed for faster generation

## Credits

Built on top of the sudoku solver from MBAI 410 Assignment 8.

**Technologies:**
- Flask - Web framework
- Vanilla JavaScript - No framework dependencies
- CSS Grid - Responsive layout

## License

See LICENSE file for details.

## Future Enhancements

Potential features for future development:
- Multiplayer/competitive mode
- Daily challenges
- Achievement system
- Custom puzzle input
- Mobile app version
- More advanced solving techniques
- Puzzle difficulty rating system

---

Enjoy playing Sudoku! 🎮
