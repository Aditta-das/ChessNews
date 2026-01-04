// Chess arrow functionality - multiple arrows
function initChessArrows(boardEl, color = 'red') {
    let isDrawing = false;
    let startSquare = null;
    let arrows = []; // Store all arrows

    // Disable context menu
    boardEl.addEventListener('contextmenu', e => e.preventDefault());

    // Helper to get square from mouse event
    function getSquareFromMouseEvent(e) {
        const rect = boardEl.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const squareSize = rect.width / 8;
        const file = Math.floor(x / squareSize);
        const rank = 7 - Math.floor(y / squareSize);
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        if (file >= 0 && file <= 7 && rank >= 0 && rank <= 7) {
            return files[file] + (rank + 1);
        }
        return null;
    }

    function drawArrow(start, end) {
        const startEl = boardEl.querySelector(`.square-${start}`);
        const endEl = boardEl.querySelector(`.square-${end}`);
        if (!startEl || !endEl) return null;

        const startRect = startEl.getBoundingClientRect();
        const endRect = endEl.getBoundingClientRect();
        const boardRect = boardEl.getBoundingClientRect();

        const x1 = startRect.left + startRect.width / 2 - boardRect.left;
        const y1 = startRect.top + startRect.height / 2 - boardRect.top;
        const x2 = endRect.left + endRect.width / 2 - boardRect.left;
        const y2 = endRect.top + endRect.height / 2 - boardRect.top;

        const dx = x2 - x1;
        const dy = y2 - y1;
        const length = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;

        const arrow = document.createElement('div');
        arrow.classList.add('arrow');
        arrow.style.width = length + 'px';
        arrow.style.left = x1 + 'px';
        arrow.style.top = y1 + 'px';
        arrow.style.transform = `rotate(${angle}deg)`;
        arrow.style.backgroundColor = color;
        arrow.style.zIndex = '1000';
        
        // Store arrow data for persistence
        arrow.dataset.start = start;
        arrow.dataset.end = end;
        arrow.dataset.color = color;

        boardEl.appendChild(arrow);
        arrows.push(arrow);
        return arrow;
    }

    function clearAllArrows() {
        arrows.forEach(arrow => {
            if (arrow && arrow.parentNode) {
                arrow.parentNode.removeChild(arrow);
            }
        });
        arrows = [];
    }

    function clearLastArrow() {
        if (arrows.length > 0) {
            const lastArrow = arrows.pop();
            if (lastArrow && lastArrow.parentNode) {
                lastArrow.parentNode.removeChild(lastArrow);
            }
        }
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            clearAllArrows();
        } else if (e.key === 'z' && e.ctrlKey) {
            e.preventDefault();
            clearLastArrow();
        }
    });

    boardEl.addEventListener('mousedown', e => {
        if (e.button === 2) { // right-click to start drawing
            startSquare = getSquareFromMouseEvent(e);
            isDrawing = !!startSquare;
            if (isDrawing) {
                e.preventDefault();
            }
        }
    });

    boardEl.addEventListener('mouseup', e => {
        if (e.button === 2 && isDrawing) {
            const endSquare = getSquareFromMouseEvent(e);
            if (endSquare && endSquare !== startSquare) {
                drawArrow(startSquare, endSquare);
            }
            isDrawing = false;
            startSquare = null;
        }
    });

    // Double right-click to clear all arrows
    let clickTimer = null;
    boardEl.addEventListener('click', e => {
        if (e.button === 2) { // right-click
            if (clickTimer === null) {
                clickTimer = setTimeout(() => {
                    clickTimer = null;
                }, 300);
            } else {
                clearTimeout(clickTimer);
                clickTimer = null;
                clearAllArrows();
            }
        }
    });

    // Handle board resize and flip
    function redrawArrows() {
        const currentArrows = [...arrows];
        clearAllArrows();
        
        // Re-draw all arrows on new board position
        currentArrows.forEach(arrowData => {
            const arrow = document.createElement('div');
            arrow.classList.add('arrow');
            arrow.dataset.start = arrowData.dataset.start;
            arrow.dataset.end = arrowData.dataset.end;
            arrow.dataset.color = arrowData.dataset.color;
            
            // Get current positions
            const startEl = boardEl.querySelector(`.square-${arrowData.dataset.start}`);
            const endEl = boardEl.querySelector(`.square-${arrowData.dataset.end}`);
            
            if (startEl && endEl) {
                const startRect = startEl.getBoundingClientRect();
                const endRect = endEl.getBoundingClientRect();
                const boardRect = boardEl.getBoundingClientRect();

                const x1 = startRect.left + startRect.width / 2 - boardRect.left;
                const y1 = startRect.top + startRect.height / 2 - boardRect.top;
                const x2 = endRect.left + endRect.width / 2 - boardRect.left;
                const y2 = endRect.top + endRect.height / 2 - boardRect.top;

                const dx = x2 - x1;
                const dy = y2 - y1;
                const length = Math.sqrt(dx * dx + dy * dy);
                const angle = Math.atan2(dy, dx) * 180 / Math.PI;

                arrow.style.width = length + 'px';
                arrow.style.left = x1 + 'px';
                arrow.style.top = y1 + 'px';
                arrow.style.transform = `rotate(${angle}deg)`;
                arrow.style.backgroundColor = arrowData.dataset.color || color;
                arrow.style.zIndex = '1000';

                boardEl.appendChild(arrow);
                arrows.push(arrow);
            }
        });
    }

    // Return control functions
    return {
        clearAllArrows: clearAllArrows,
        clearLastArrow: clearLastArrow,
        redrawArrows: redrawArrows
    };
}