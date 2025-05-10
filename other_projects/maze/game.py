from maze import Maze
from player import Player
from gamestats import GameStats
from ui import UI

class Game:
    def __init__(self):
        self.maze = Maze(20, min_distance=6)  # Increased difficulty with a larger maze
        self.player = Player(self.maze)
        self.stats = GameStats()
        self.ui = UI(self)

    def run(self):
        while not self.player.has_won and self.player.get_moves_left() > 0:
            self.ui.handle_input()
            self.ui.draw_maze()
            if self.player.has_won_game():
                self.stats.record_win()
                self.stats.update_stats(20 - self.player.get_moves_left())
                print("You won!")
                break
        else:
            print("Game Over! You ran out of moves.")
        print(self.stats.get_stats())

if __name__ == "__main__":
    game = Game()
    game.run()
