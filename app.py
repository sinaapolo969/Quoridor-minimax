import pygame
import time
from copy import deepcopy
from environment import Board 

# Constants
CELL_SIZE = 60
WINDOW_WIDTH = CELL_SIZE * 9 + 200
WINDOW_HEIGHT = CELL_SIZE * 9
UI_COLOR = (240, 240, 240)
PLAYER_COLORS = {1: (255, 0, 0), 2: (0, 0, 255)}
WALL_COLOR = (100, 100, 100)

def minimax_decision(board, depth, player):
    """Wrapper function to initiate minimax and return the best move."""
    def get_all_moves(board, player):
        """Get all possible moves (pawn and walls) for the player."""
        moves = []
        # Pawn moves
        for move in board.get_all_valid_moves(player):
            moves.append(("move", move))
        # Wall placements
        for wall in board.get_all_valid_wall_placements(player):
            moves.append(("wall", wall))
        return moves

    def minimax(board, depth, player, alpha=float("-inf"), beta=float("inf")):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0 or board.is_game_over():
            return board.evaluate(), None

        best_move = None
        valid_moves = get_all_moves(board, player)

        if player == 1:  # Maximizing player (AI)
            max_eval = float("-inf")
            for move_type, move in valid_moves:
                temp_board = deepcopy(board)
                if move_type == "move":
                    temp_board.move_player(player, move)
                elif move_type == "wall":
                    temp_board.add_wall(move, player)
                eval, _ = minimax(temp_board, depth - 1, 2, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (move_type, move)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Minimizing player (human, but not used here)
            min_eval = float("inf")
            for move_type, move in valid_moves:
                temp_board = deepcopy(board)
                if move_type == "move":
                    temp_board.move_player(player, move)
                elif move_type == "wall":
                    temp_board.add_wall(move, player)
                eval, _ = minimax(temp_board, depth - 1, 1, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (move_type, move)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    return minimax(deepcopy(board), depth, player)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Quoridor - AI vs Human")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    board = Board()
    current_player = 1  # AI starts first
    game_over = False

    def draw_board():
        """Render the board, players, walls, and UI elements."""
        screen.fill((255, 255, 255))
        # Draw grid lines
        for i in range(9):
            pygame.draw.line(screen, (0, 0, 0), (i*CELL_SIZE, 0), (i*CELL_SIZE, WINDOW_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (0, i*CELL_SIZE), (WINDOW_WIDTH - 200, i*CELL_SIZE))
        # Draw players
        for p, (row, col) in board.players.items():
            pygame.draw.circle(screen, PLAYER_COLORS[p], 
                             (col*CELL_SIZE + CELL_SIZE//2, row*CELL_SIZE + CELL_SIZE//2), 
                             CELL_SIZE//3)
        # Draw walls
        for wall in board.walls['horizontal']:
            row, col = wall
            pygame.draw.line(screen, WALL_COLOR, 
                            (col*CELL_SIZE, (row + 1)*CELL_SIZE), 
                            ((col + 1)*CELL_SIZE, (row + 1)*CELL_SIZE), 5)
        for wall in board.walls['vertical']:
            row, col = wall
            pygame.draw.line(screen, WALL_COLOR, 
                            ((col + 1)*CELL_SIZE, row*CELL_SIZE), 
                            ((col + 1)*CELL_SIZE, (row + 1)*CELL_SIZE), 5)
        # Sidebar UI
        pygame.draw.rect(screen, UI_COLOR, (CELL_SIZE*9, 0, 200, WINDOW_HEIGHT))
        text = font.render(f'AI Walls: {board.walls_left[1]}', True, PLAYER_COLORS[1])
        screen.blit(text, (CELL_SIZE*9 + 10, 50))
        text = font.render(f'Your Walls: {board.walls_left[2]}', True, PLAYER_COLORS[2])
        screen.blit(text, (CELL_SIZE*9 + 10, 100))
        text = font.render(f'Turn: {"AI" if current_player == 1 else "You"}', True, (0, 0, 0))
        screen.blit(text, (CELL_SIZE*9 + 10, 150))
        if game_over:
            winner = 1 if board.players[1][0] == 8 else 2
            text = font.render(f'{"AI" if winner ==1 else "You"} Won!', True, (0, 200, 0))
            screen.blit(text, (CELL_SIZE*9 + 10, 200))

    running = True
    while running:
        # AI's turn (Player 1)
        if not game_over and current_player == 1:
            start_time = time.time()
            _, best_move = minimax_decision(board, depth=2, player=1)
            print(f"AI Move Time: {time.time() - start_time:.2f}s")
            if best_move:
                move_type, move = best_move
                if move_type == "move":
                    board.move_player(1, move)
                elif move_type == "wall" and board.walls_left[1] > 0:
                    board.add_wall(move, 1)
                # Check game over
                if board.is_game_over():
                    game_over = True
                else:
                    current_player = 2  # Switch to human

        # Event handling for human (Player 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and current_player == 2:
                x, y = event.pos
                # Check if the click is on the grid
                if x < CELL_SIZE * 9:
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    # Check if it's a valid pawn move
                    if (row, col) in board.get_all_valid_moves(2):
                        board.move_player(2, (row, col))
                        if board.is_game_over():
                            game_over = True
                        else:
                            current_player = 1
                    # Check for wall placement (horizontal/vertical)
                    else:
                        # Horizontal wall (click near bottom of a cell)
                        if y % CELL_SIZE > CELL_SIZE - 10:
                            wall_row = row
                            wall_col = col
                            wall_move = (wall_row, wall_col, 'horizontal')
                            if wall_move in board.get_all_valid_wall_placements(2):
                                board.add_wall(wall_move, 2)
                                current_player = 1
                        # Vertical wall (click near right of a cell)
                        elif x % CELL_SIZE > CELL_SIZE - 10:
                            wall_row = row
                            wall_col = col
                            wall_move = (wall_row, wall_col, 'vertical')
                            if wall_move in board.get_all_valid_wall_placements(2):
                                board.add_wall(wall_move, 2)
                                current_player = 1

        draw_board()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()