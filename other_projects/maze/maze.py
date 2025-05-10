import random
import math

class Maze:
    def __init__(self, size, min_distance=5):
        self.size = size
        self.grid = [[1 for _ in range(size)] for _ in range(size)]  # Start with walls
        self.start = self.generate_random_point()
        self.exit = self.generate_random_point(min_distance)
        while self.get_distance(self.start, self.exit) < min_distance:
            ### If the distance between start and exit is too small, regenerate exit point
            self.exit = self.generate_random_point(min_distance)
        self.generate_maze()

    def generate_random_point(self, min_distance=0):
        ###Generate a random point within the maze grid.
        x = random.randint(1, self.size - 2)  # Avoid edges to prevent going out of bounds
        y = random.randint(1, self.size - 2)
        return (x, y)

    def get_distance(self, point1, point2):
        ###Calculate the Euclidean distance between two points.
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def generate_maze(self):
        ### Start by carving paths from the start point
        self.carve_path(self.start[0], self.start[1])

        ### Ensure the start and exit points are open
        self.grid[self.start[1]][self.start[0]] = 0  # Start position
        self.grid[self.exit[1]][self.exit[0]] = 0  # Exit position

    def carve_path(self, x, y):
        ###Recursively carve a path using backtracking.
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  
        random.shuffle(directions)  # Shuffle to create varied paths

        for dx, dy in directions:
            nx, ny = x + dx*2, y + dy*2

            if 0 < nx < self.size - 1 and 0 < ny < self.size - 1 and self.grid[ny][nx] == 1:
                ### Check if the cell is within bounds and is a wall
                ### Carve a passage by marking it as 0
                self.grid[ny][nx] = 0
                ### After carving a passage, also carve a wall next to it to avoid loops
                self.grid[y + dy][x + dx] = 0  # Carve walls between passages
                ### Recursively continue carving
                self.carve_path(nx, ny)

    def ensure_path(self):
        pass
