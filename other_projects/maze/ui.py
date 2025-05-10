import pygame
import sys

class UI:
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.screen_size = 600
        self.cell_size = self.screen_size // self.game.maze.size
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Escape the Maze")
        self.font = pygame.font.Font(None, 36)

    def draw_maze(self):
        self.screen.fill((0, 0, 0))
        for y in range(self.game.maze.size):
            for x in range(self.game.maze.size):
                color = (255, 255, 255) if self.game.maze.grid[y][x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

        # Player in green
        pygame.draw.rect(self.screen, (0, 255, 0), (self.game.player.x * self.cell_size, self.game.player.y * self.cell_size, self.cell_size, self.cell_size))
        ### Exit Point
        exit_x, exit_y = self.game.maze.exit
        pygame.draw.rect(self.screen, (255,0,0), (exit_x * self.cell_size, exit_y * self.cell_size, self.cell_size, self.cell_size))

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.game.player.move('w')
                elif event.key == pygame.K_s:
                    self.game.player.move('s')
                elif event.key == pygame.K_a:
                    self.game.player.move('a')
                elif event.key == pygame.K_d:
                    self.game.player.move('d')
                self.draw_maze()
