
class Board:
    def __init__(self):
        """Initialize the Quoridor board and its attributes."""
        self.size = 9  # Quoridor board is a 9x9 grid
        self.board = [["." for _ in range(self.size)] for _ in range(self.size)]  # Initialize empty grid
        self.walls = {"horizontal": set(), "vertical": set()}  # Store wall positions
        self.players = {1: (0, 4), 2: (8, 4)}  # Default starting positions for players (row, column)
        self.walls_left = {1: 10, 2: 10}  # Number of walls left for each player

    def is_within_bounds(self, row, col):
        """Check if a position is within the board boundaries."""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def evaluate(self):
        """
        Evaluate the board state from the perspective of Player 1.
        Improved to consider path difference, wall advantage, and opponent proximity.
        """
        from collections import deque

        def shortest_path(player, goal_row):
            """BFS to find shortest path for a player to their goal row."""
            start_row, start_col = self.players[player]
            visited = set()
            queue = deque([(start_row, start_col, 0)])  # (row, col, distance)
            shortest_distance = float("inf")

            while queue:
                row, col, dist = queue.popleft()  # Use BFS (FIFO)

                if (row, col) in visited:
                    continue
                visited.add((row, col))

                # Check if goal reached
                if row == goal_row:
                    shortest_distance = dist
                    break  # BFS guarantees shortest path

                # Get valid moves without modifying the board state
                valid_moves = []
                current_pos = (row, col)
                # Check all possible moves (up, down, left, right)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if self.is_within_bounds(new_row, new_col):
                        # Check for walls blocking the move
                        if dr == -1:  # Up
                            if (row - 1, col) not in self.walls["horizontal"]:
                                valid_moves.append((new_row, new_col))
                        elif dr == 1:  # Down
                            if (row, col) not in self.walls["horizontal"]:
                                valid_moves.append((new_row, new_col))
                        elif dc == -1:  # Left
                            if (row, col - 1) not in self.walls["vertical"]:
                                valid_moves.append((new_row, new_col))
                        elif dc == 1:  # Right
                            if (row, col) not in self.walls["vertical"]:
                                valid_moves.append((new_row, new_col))

                for move in valid_moves:
                    if move not in visited:
                        queue.append((move[0], move[1], dist + 1))

            return shortest_distance if shortest_distance != float("inf") else float("inf")

        # Calculate shortest paths
        p1_distance = shortest_path(1, 8)  # Player 1's goal: row 8
        p2_distance = shortest_path(2, 0)  # Player 2's goal: row 0

        # Base score: Favor shorter agent path and longer opponent path
        base_score = p2_distance - p1_distance

        # Wall advantage: Encourage saving/using walls strategically
        wall_weight = 2  # Tune this value based on testing
        wall_score = (self.walls_left[1] - self.walls_left[2]) * wall_weight

        # Opponent proximity penalty: Penalize if opponent is close to winning
        opponent_penalty = 0
        if p2_distance <= 3:  # If opponent is within 3 steps of goal
            opponent_penalty = -15 * (4 - p2_distance)  # Exponential penalty

        # Check for game-ending conditions
        if p1_distance == float("inf"):
            return -float("inf")  # Agent has no path (worst case)
        if p2_distance == float("inf"):
            return float("inf")  # Opponent has no path (best case)

        # Combine all factors
        total_score = base_score + wall_score + opponent_penalty
        return total_score

    def add_wall(self, move, player):
        """
        Add a wall to the board.
        
        Args:
            wall_type (str): "horizontal" or "vertical".
            position (tuple): Starting position of the wall (row, col).
        
        Returns:
            bool: True if the wall was added successfully, False otherwise.
        """
        position = move[:2]
        wall_type = move[2]
        if wall_type not in self.walls:
            return False

        if wall_type == "horizontal":
            if (self.is_within_bounds(position[0], position[1]) and 
                self.is_within_bounds(position[0], position[1] + 1)):
                if (position not in self.walls["horizontal"] and 
                    (position[0], position[1] + 1) not in self.walls["horizontal"]):
                    self.walls["horizontal"].add(position)
                    self.walls["horizontal"].add((position[0], position[1] + 1))
                    self.walls_left[player] -= 1
                    return True
        elif wall_type == "vertical":
            if (self.is_within_bounds(position[0], position[1]) and 
                self.is_within_bounds(position[0] + 1, position[1])):
                if (position not in self.walls["vertical"] and 
                    (position[0] + 1, position[1]) not in self.walls["vertical"]):
                    self.walls["vertical"].add(position)
                    self.walls["vertical"].add((position[0] + 1, position[1]))
                    self.walls_left[player] -= 1
                    return True

        return False

    def move_player(self, player, new_position):
        """
        Move a player to a new position.

        Args:
            player (int): Player number (1 or 2).
            new_position (tuple): New position (row, col).

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if player not in self.players:
            return False

        if self.is_within_bounds(new_position[0], new_position[1]):
            self.players[player] = new_position
            return True

        return False

    def get_all_valid_moves(self, player, current_position_temp=None):
        """
        Get all valid moves for a given player.

        Args:
            player (int): Player number (1 or 2).

        Returns:
            list: A list of valid moves as tuples (row, col).
        """
        if player not in self.players:
            return []

        current_position = self.players[player]
        row, col = current_position
        if current_position_temp:
            row, col = current_position_temp

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        valid_moves = []

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_within_bounds(new_row, new_col):
                # Check for walls in the direction of movement
                if dr == -1 and (row - 1, col) not in self.walls["horizontal"]:  # Up
                    valid_moves.append((new_row, new_col))
                elif dr == 1 and (row, col) not in self.walls["horizontal"]:  # Down
                    valid_moves.append((new_row, new_col))
                elif dc == -1 and (row, col - 1) not in self.walls["vertical"]:  # Left
                    valid_moves.append((new_row, new_col))
                elif dc == 1 and (row, col) not in self.walls["vertical"]:  # Right
                    valid_moves.append((new_row, new_col))

        return valid_moves
    
    def get_all_valid_wall_placements(self, player):
        if self.walls_left[player] == 0:
            return []
        valid_wall_placements = []
        
        # Check horizontal walls (placed between rows, spanning two columns)
        for row in range(self.size - 1):
            for col in range(self.size - 1):
                # Check if the two cells for the horizontal wall are available
                if ((row, col) not in self.walls["horizontal"] and
                    (row, col + 1) not in self.walls["horizontal"] and
                    # Ensure no overlapping vertical walls
                    (row, col) not in self.walls["vertical"] and
                    (row, col + 1) not in self.walls["vertical"]):
                    
                    # Temporarily add the horizontal wall
                    self.walls["horizontal"].add((row, col))
                    self.walls["horizontal"].add((row, col + 1))
                    
                    if self.is_path_valid():
                        valid_wall_placements.append((row, col, "horizontal"))
                    
                    # Remove temporary wall
                    self.walls["horizontal"].remove((row, col))
                    self.walls["horizontal"].remove((row, col + 1))
        
        # Check vertical walls (placed between columns, spanning two rows)
        for row in range(self.size - 1):
            for col in range(self.size - 1):
                # Check if the two cells for the vertical wall are available
                if ((row, col) not in self.walls["vertical"] and
                    (row + 1, col) not in self.walls["vertical"] and
                    # Ensure no overlapping horizontal walls
                    (row, col) not in self.walls["horizontal"] and
                    (row + 1, col) not in self.walls["horizontal"]):
                    
                    # Temporarily add the vertical wall
                    self.walls["vertical"].add((row, col))
                    self.walls["vertical"].add((row + 1, col))
                    
                    if self.is_path_valid():
                        valid_wall_placements.append((row, col, "vertical"))
                    
                    # Remove temporary wall
                    self.walls["vertical"].remove((row, col))
                    self.walls["vertical"].remove((row + 1, col))
        
        return valid_wall_placements

    def is_path_valid(self):
        """Check if both players have a valid path to their goals."""
        from collections import deque
        
        def bfs(player, start_row, start_col, goal_row):
            visited = set()
            queue = deque([(start_row, start_col)])
            
            while queue:
                row, col = queue.popleft()
                if (row, col) in visited:
                    continue
                visited.add((row, col))
                
                if row == goal_row:
                    return True  # Path exists
                
                # Check all possible moves (up, down, left, right)
                # Up
                if row > 0 and (row - 1, col) not in self.walls["horizontal"]:
                    if (row - 1, col) not in visited:
                        queue.append((row - 1, col))
                # Down
                if row < self.size - 1 and (row, col) not in self.walls["horizontal"]:
                    if (row + 1, col) not in visited:
                        queue.append((row + 1, col))
                # Left
                if col > 0 and (row, col - 1) not in self.walls["vertical"]:
                    if (row, col - 1) not in visited:
                        queue.append((row, col - 1))
                # Right
                if col < self.size - 1 and (row, col) not in self.walls["vertical"]:
                    if (row, col + 1) not in visited:
                        queue.append((row, col + 1))
            
            return False  # No path
        
        # Check paths for both players
        p1_start = self.players[1]
        p2_start = self.players[2]
        p1_has_path = bfs(1, p1_start[0], p1_start[1], 8)
        p2_has_path = bfs(2, p2_start[0], p2_start[1], 0)
        
        return p1_has_path and p2_has_path
        

    def is_game_over(self):
        """Check if the game has ended."""
        for player, position in self.players.items():
            if player == 1 and position[0] == 8:
                return True
            if player == 2 and position[0] == 0:
                return True
        return False


    def display(self):
        """Display the current state of the board."""
        # Create a copy of the board to display walls and players
        display_board = [["." for _ in range(self.size)] for _ in range(self.size)]

        # Place players on the board
        for player, position in self.players.items():
            display_board[position[0]][position[1]] = str(player)

        # Display the board with walls
        for row in range(self.size):
            row_display = ""
            for col in range(self.size):
                row_display += display_board[row][col]
                if (row, col) in self.walls["vertical"]:
                    row_display += "|"  # Vertical wall
                else:
                    row_display += " "
            print(row_display)
            if row < self.size - 1:
                horizontal_row = ""
                for col in range(self.size):
                    if (row, col) in self.walls["horizontal"]:
                        horizontal_row += "__"
                    else:
                        horizontal_row += "  "
                print(horizontal_row)



