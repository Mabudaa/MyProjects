class GameStats:
    def __init__(self):
        self.games_played = 0
        self.games_won = 0
        self.fastest_win = float('inf')

    def update_stats(self, moves_taken):
        self.games_played += 1
        if moves_taken < self.fastest_win:
            self.fastest_win = moves_taken

    def record_win(self):
        self.games_won += 1

    def get_stats(self):
        win_rate = (self.games_won / self.games_played) * 100 if self.games_played > 0 else 0
        return f"Games Played: {self.games_played}, Wins: {self.games_won}, Win Rate: {win_rate:.2f}%, Fastest Win: {self.fastest_win} moves"
