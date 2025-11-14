// ================================
// Game State Management
// ================================

class SudokuGame {
    constructor() {
        this.sessionId = null;
        this.board = this.createEmptyBoard();
        this.initialBoard = this.createEmptyBoard();
        this.solution = null;
        this.selectedCell = null;
        this.lives = 3;
        this.startTime = null;
        this.elapsedTime = 0;
        this.timerInterval = null;
        this.score = 0;
        this.difficulty = 'medium';
        this.pencilMode = false;
        this.pencilMarks = this.createEmptyPencilMarks();
        this.history = [];
        this.historyIndex = -1;
        this.hintsUsed = 0;
        this.gameActive = false;

        this.initializeEventListeners();
        this.loadTheme();
    }

    createEmptyBoard() {
        return Array(9).fill(null).map(() => Array(9).fill(0));
    }

    createEmptyPencilMarks() {
        return Array(9).fill(null).map(() =>
            Array(9).fill(null).map(() => new Set())
        );
    }

    // ================================
    // API Communication
    // ================================

    async startNewGame(difficulty) {
        try {
            const response = await fetch('/api/new-puzzle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ difficulty })
            });

            const data = await response.json();

            this.sessionId = data.session_id;
            this.board = data.puzzle;
            this.initialBoard = data.puzzle.map(row => [...row]);
            this.difficulty = difficulty;
            this.lives = 3;
            this.startTime = Date.now();
            this.elapsedTime = 0;
            this.score = 0;
            this.hintsUsed = 0;
            this.pencilMarks = this.createEmptyPencilMarks();
            this.history = [];
            this.historyIndex = -1;
            this.gameActive = true;

            this.saveState();
            this.renderBoard();
            this.updateStats();
            this.startTimer();
            this.showGameBoard();

        } catch (error) {
            console.error('Error starting new game:', error);
            alert('Failed to start new game. Please try again.');
        }
    }

    async validateMove(row, col, value) {
        try {
            const response = await fetch('/api/validate-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    row: row,
                    col: col,
                    value: value,
                    current_board: this.board
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error validating move:', error);
            return { valid: false, reason: 'error' };
        }
    }

    async getSolution() {
        try {
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const data = await response.json();
            return data.solution;
        } catch (error) {
            console.error('Error getting solution:', error);
            return null;
        }
    }

    async getHint() {
        try {
            const response = await fetch('/api/hint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    current_board: this.board
                })
            });

            const data = await response.json();

            if (data.error) {
                alert('No hints available!');
                return null;
            }

            return data;
        } catch (error) {
            console.error('Error getting hint:', error);
            return null;
        }
    }

    // ================================
    // Game Logic
    // ================================

    async placeNumber(row, col, value) {
        if (!this.gameActive) return;
        if (this.initialBoard[row][col] !== 0) return;

        // If in pencil mode, toggle pencil mark
        if (this.pencilMode) {
            this.togglePencilMark(row, col, value);
            return;
        }

        // Store the old value and pencil marks in case we need to revert
        const oldValue = this.board[row][col];
        const oldPencilMarks = new Set(this.pencilMarks[row][col]);

        // Temporarily place the number for validation
        this.board[row][col] = value;

        // Validate the move
        const validation = await this.validateMove(row, col, value);

        if (!validation.valid) {
            // REVERT THE MOVE - board should never be in unsolvable state
            this.board[row][col] = oldValue;
            this.pencilMarks[row][col] = oldPencilMarks;

            // Flash conflict animation on the cell
            const cellElement = document.querySelector(
                `.cell[data-row="${row}"][data-col="${col}"]`
            );
            if (cellElement) {
                cellElement.classList.add('conflict');
                setTimeout(() => cellElement.classList.remove('conflict'), 400);
            }

            // Show alert and lose a life
            this.loseLife(validation.message);

            // Re-render with reverted state
            this.renderBoard();
            this.updateStats();

        } else {
            // Valid move - commit it by saving state
            this.saveState();

            // Clear pencil marks for this cell
            this.pencilMarks[row][col].clear();

            // Flash correct animation
            const cellElement = document.querySelector(
                `.cell[data-row="${row}"][data-col="${col}"]`
            );
            if (cellElement) {
                cellElement.classList.add('correct-flash');
                setTimeout(() => cellElement.classList.remove('correct-flash'), 500);
            }

            // Update score
            this.updateScore(10);

            // Update UI
            this.renderBoard();
            this.updateStats();
            this.checkWin();
        }
    }

    togglePencilMark(row, col, value) {
        if (this.board[row][col] !== 0) return;

        if (this.pencilMarks[row][col].has(value)) {
            this.pencilMarks[row][col].delete(value);
        } else {
            this.pencilMarks[row][col].add(value);
        }

        this.renderBoard();
    }

    eraseCell(row, col) {
        if (!this.gameActive) return;
        if (this.initialBoard[row][col] !== 0) return;

        this.saveState();
        this.board[row][col] = 0;
        this.pencilMarks[row][col].clear();
        this.renderBoard();
    }

    async useHint() {
        if (!this.gameActive) return;

        const hint = await this.getHint();
        if (!hint) return;

        this.saveState();
        this.hintsUsed++;
        this.board[hint.row][hint.col] = hint.value;
        this.pencilMarks[hint.row][hint.col].clear();

        // Highlight the hint cell
        const cellElement = document.querySelector(
            `.cell[data-row="${hint.row}"][data-col="${hint.col}"]`
        );
        if (cellElement) {
            cellElement.classList.add('correct-flash');
            setTimeout(() => cellElement.classList.remove('correct-flash'), 500);
        }

        // Penalty: reduce score
        this.updateScore(-20);

        this.renderBoard();
        this.updateStats();
        this.checkWin();
    }

    async solvePuzzle() {
        if (!this.gameActive) return;

        const solution = await this.getSolution();
        if (!solution) {
            alert('Unable to solve puzzle');
            return;
        }

        this.board = solution;
        this.gameActive = false;
        this.stopTimer();
        this.renderBoard();

        setTimeout(() => {
            this.showGameOver('Puzzle Solved', 'The puzzle has been solved for you!', false);
        }, 500);
    }

    loseLife(message) {
        this.lives--;
        this.updateScore(-15);
        this.updateStats();

        if (this.lives <= 0) {
            this.gameOver();
        } else {
            // Show temporary message
            this.showNotification(message || 'Incorrect move! Life lost.', 'error');
        }
    }

    async gameOver() {
        this.gameActive = false;
        this.stopTimer();

        const solution = await this.getSolution();
        if (solution) {
            this.board = solution;
            this.renderBoard();
        }

        setTimeout(() => {
            this.showGameOver('Game Over!', 'You ran out of lives.', false);
        }, 500);
    }

    checkWin() {
        // Check if board is completely filled
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (this.board[row][col] === 0) return;
            }
        }

        // Board is filled - player won!
        this.gameActive = false;
        this.stopTimer();
        this.calculateFinalScore();

        setTimeout(() => {
            this.showVictory();
        }, 500);
    }

    // ================================
    // History (Undo/Redo)
    // ================================

    saveState() {
        const state = {
            board: this.board.map(row => [...row]),
            pencilMarks: this.pencilMarks.map(row =>
                row.map(cell => new Set(cell))
            ),
            score: this.score
        };

        // Remove any states after current index
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex++;

        // Limit history size
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }

        this.updateUndoRedoButtons();
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            const state = this.history[this.historyIndex];
            this.board = state.board.map(row => [...row]);
            this.pencilMarks = state.pencilMarks.map(row =>
                row.map(cell => new Set(cell))
            );
            this.score = state.score;
            this.renderBoard();
            this.updateStats();
            this.updateUndoRedoButtons();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            const state = this.history[this.historyIndex];
            this.board = state.board.map(row => [...row]);
            this.pencilMarks = state.pencilMarks.map(row =>
                row.map(cell => new Set(cell))
            );
            this.score = state.score;
            this.renderBoard();
            this.updateStats();
            this.updateUndoRedoButtons();
        }
    }

    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');

        undoBtn.disabled = this.historyIndex <= 0;
        redoBtn.disabled = this.historyIndex >= this.history.length - 1;
    }

    // ================================
    // Timer and Scoring
    // ================================

    startTimer() {
        this.stopTimer();
        this.timerInterval = setInterval(() => {
            this.elapsedTime = Date.now() - this.startTime;
            this.updateTimerDisplay();
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    updateTimerDisplay() {
        const seconds = Math.floor(this.elapsedTime / 1000);
        const minutes = Math.floor(seconds / 60);
        const displaySeconds = seconds % 60;

        document.getElementById('timer').textContent =
            `${String(minutes).padStart(2, '0')}:${String(displaySeconds).padStart(2, '0')}`;
    }

    updateScore(delta) {
        this.score = Math.max(0, this.score + delta);
        document.getElementById('score').textContent = this.score;
    }

    calculateFinalScore() {
        const timeBonus = Math.max(0, 1000 - Math.floor(this.elapsedTime / 1000));
        const livesBonus = this.lives * 100;
        const hintPenalty = this.hintsUsed * 50;

        this.score += timeBonus + livesBonus - hintPenalty;
        this.score = Math.max(0, this.score);
    }

    // ================================
    // UI Updates
    // ================================

    renderBoard() {
        const boardElement = document.getElementById('sudoku-board');
        boardElement.innerHTML = '';

        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;

                const isGiven = this.initialBoard[row][col] !== 0;
                if (isGiven) {
                    cell.classList.add('given');
                }

                if (this.selectedCell &&
                    this.selectedCell.row === row &&
                    this.selectedCell.col === col) {
                    cell.classList.add('selected');
                }

                const value = this.board[row][col];
                if (value !== 0) {
                    cell.textContent = value;
                } else if (this.pencilMarks[row][col].size > 0) {
                    // Show pencil marks
                    const marksContainer = document.createElement('div');
                    marksContainer.className = 'pencil-marks';

                    for (let i = 1; i <= 9; i++) {
                        const mark = document.createElement('div');
                        mark.className = 'pencil-mark';
                        if (this.pencilMarks[row][col].has(i)) {
                            mark.textContent = i;
                        }
                        marksContainer.appendChild(mark);
                    }

                    cell.appendChild(marksContainer);
                }

                cell.addEventListener('click', () => this.selectCell(row, col));
                boardElement.appendChild(cell);
            }
        }
    }

    selectCell(row, col) {
        this.selectedCell = { row, col };
        this.renderBoard();
    }

    updateStats() {
        // Update lives
        const hearts = document.querySelectorAll('.heart');
        hearts.forEach((heart, index) => {
            if (index >= this.lives) {
                heart.classList.add('lost');
            } else {
                heart.classList.remove('lost');
            }
        });

        // Update score
        document.getElementById('score').textContent = this.score;
    }

    showGameBoard() {
        document.getElementById('difficulty-container').style.display = 'none';
        document.getElementById('board-container').style.display = 'block';
        document.getElementById('controls-container').style.display = 'flex';
        document.getElementById('number-pad').style.display = 'grid';
    }

    showDifficultySelection() {
        document.getElementById('difficulty-container').style.display = 'block';
        document.getElementById('board-container').style.display = 'none';
        document.getElementById('controls-container').style.display = 'none';
        document.getElementById('number-pad').style.display = 'none';
        this.stopTimer();
    }

    showGameOver(title, message, isVictory) {
        const modal = document.getElementById('game-over-modal');
        document.getElementById('game-over-title').textContent = title;
        document.getElementById('game-over-message').textContent = message;

        const statsHtml = `
            <p><strong>Time:</strong> ${document.getElementById('timer').textContent}</p>
            <p><strong>Final Score:</strong> ${this.score}</p>
            <p><strong>Difficulty:</strong> ${this.difficulty.charAt(0).toUpperCase() + this.difficulty.slice(1)}</p>
        `;
        document.getElementById('game-over-stats').innerHTML = statsHtml;

        modal.classList.add('show');
    }

    showVictory() {
        const modal = document.getElementById('victory-modal');

        const statsHtml = `
            <p><strong>Time:</strong> ${document.getElementById('timer').textContent}</p>
            <p><strong>Final Score:</strong> ${this.score}</p>
            <p><strong>Lives Remaining:</strong> ${this.lives}</p>
            <p><strong>Hints Used:</strong> ${this.hintsUsed}</p>
            <p><strong>Difficulty:</strong> ${this.difficulty.charAt(0).toUpperCase() + this.difficulty.slice(1)}</p>
        `;
        document.getElementById('victory-stats').innerHTML = statsHtml;

        modal.classList.add('show');
    }

    hideModals() {
        document.getElementById('game-over-modal').classList.remove('show');
        document.getElementById('victory-modal').classList.remove('show');
    }

    showNotification(message, type = 'info') {
        // Simple alert for now - can be enhanced with toast notifications
        alert(message);
    }

    // ================================
    // Theme Management
    // ================================

    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('sudoku-theme', newTheme);

        // Update theme icon
        const themeIcon = document.querySelector('.theme-icon');
        themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('sudoku-theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);

        const themeIcon = document.querySelector('.theme-icon');
        themeIcon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }

    // ================================
    // Event Listeners
    // ================================

    initializeEventListeners() {
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Difficulty selection
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const difficulty = btn.dataset.difficulty;
                this.startNewGame(difficulty);
            });
        });

        // Number pad
        document.querySelectorAll('.number-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (this.selectedCell) {
                    const value = parseInt(btn.dataset.number);
                    this.placeNumber(this.selectedCell.row, this.selectedCell.col, value);
                }
            });
        });

        // Controls
        document.getElementById('pencil-mode-btn').addEventListener('click', () => {
            this.pencilMode = !this.pencilMode;
            document.getElementById('pencil-mode-btn').classList.toggle('active', this.pencilMode);
        });

        document.getElementById('erase-btn').addEventListener('click', () => {
            if (this.selectedCell) {
                this.eraseCell(this.selectedCell.row, this.selectedCell.col);
            }
        });

        document.getElementById('undo-btn').addEventListener('click', () => {
            this.undo();
        });

        document.getElementById('redo-btn').addEventListener('click', () => {
            this.redo();
        });

        document.getElementById('hint-btn').addEventListener('click', () => {
            this.useHint();
        });

        document.getElementById('solve-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to solve the puzzle? This will end the game.')) {
                this.solvePuzzle();
            }
        });

        document.getElementById('new-game-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to start a new game? Current progress will be lost.')) {
                this.hideModals();
                this.showDifficultySelection();
            }
        });

        document.getElementById('restart-btn').addEventListener('click', () => {
            this.hideModals();
            this.showDifficultySelection();
        });

        document.getElementById('victory-new-game-btn').addEventListener('click', () => {
            this.hideModals();
            this.showDifficultySelection();
        });

        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            this.handleKeyPress(e);
        });
    }

    handleKeyPress(e) {
        if (!this.gameActive || !this.selectedCell) return;

        const { row, col } = this.selectedCell;

        // Number keys (1-9)
        if (e.key >= '1' && e.key <= '9') {
            e.preventDefault();
            const value = parseInt(e.key);
            this.placeNumber(row, col, value);
        }

        // Delete/Backspace
        if (e.key === 'Delete' || e.key === 'Backspace') {
            e.preventDefault();
            this.eraseCell(row, col);
        }

        // Arrow keys
        if (e.key === 'ArrowUp' && row > 0) {
            e.preventDefault();
            this.selectCell(row - 1, col);
        }
        if (e.key === 'ArrowDown' && row < 8) {
            e.preventDefault();
            this.selectCell(row + 1, col);
        }
        if (e.key === 'ArrowLeft' && col > 0) {
            e.preventDefault();
            this.selectCell(row, col - 1);
        }
        if (e.key === 'ArrowRight' && col < 8) {
            e.preventDefault();
            this.selectCell(row, col + 1);
        }

        // P for pencil mode
        if (e.key === 'p' || e.key === 'P') {
            e.preventDefault();
            this.pencilMode = !this.pencilMode;
            document.getElementById('pencil-mode-btn').classList.toggle('active', this.pencilMode);
        }

        // Z for undo (Ctrl+Z or Cmd+Z)
        if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
            e.preventDefault();
            if (e.shiftKey) {
                this.redo();
            } else {
                this.undo();
            }
        }
    }
}

// ================================
// Initialize Game
// ================================

let game;

document.addEventListener('DOMContentLoaded', () => {
    game = new SudokuGame();
});
