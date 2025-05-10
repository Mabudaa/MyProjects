class Player:
    def __init__(self, maze):
        self.maze = maze
        self.x, self.y = maze.start
        self.moves_left = 50  # Limited moves to win
        self.has_won = False

    def move(self, direction):
        if self.moves_left <= 0:
            return  # No more moves left

        dx, dy = 0, 0
        if direction == 'w': dy = -1
        elif direction == 's': dy = 1
        elif direction == 'a': dx = -1
        elif direction == 'd': dx = 1

        new_x, new_y = self.x + dx, self.y + dy

        # Check if the move is within bounds and not a wall
        if 0 <= new_x < self.maze.size and 0 <= new_y < self.maze.size and self.maze.grid[new_y][new_x] == 0:
            self.x, self.y = new_x, new_y
            self.moves_left -= 1

            # Check if player reached the exit
            if (self.x, self.y) == self.maze.exit:
                self.has_won = True

    def get_moves_left(self):
        return self.moves_left

    def has_won_game(self):
        return self.has_won
