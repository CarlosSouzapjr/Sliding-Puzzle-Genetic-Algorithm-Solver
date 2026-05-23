import numpy as np


class GameLogic:
    def __init__(self, size):
        self.size = size
        self.board = np.arange(1, size*size + 1).reshape(size, size)
        self.empty_pos = [size - 1, size - 1]
        self.directions = ['up', 'down', 'left', 'right']

    def move(self, direction):
        r, l = self.empty_pos
        if direction == 'up' and r > 0:
            self.board[r, l], self.board[r-1, l] = self.board[r-1, l], self.board[r, l]
            self.empty_pos[0] -= 1
        elif direction == 'down' and r < self.size - 1:
            self.board[r, l], self.board[r+1, l] = self.board[r+1, l], self.board[r, l]
            self.empty_pos[0] += 1
        elif direction == 'left' and l > 0:
            self.board[r, l], self.board[r, l-1] = self.board[r, l-1], self.board[r, l]
            self.empty_pos[1] -= 1
        elif direction == 'right' and l < self.size - 1:
            self.board[r, l], self.board[r, l+1] = self.board[r, l+1], self.board[r, l]
            self.empty_pos[1] += 1

    def is_solved(self):
        return np.array_equal(self.board.flatten(), np.arange(1, self.size*self.size + 1))
    
    def randomize(self, moves=100):
        for _ in range(moves):
            self.move(np.random.choice(self.directions))

    def play_moves(self, moves):
        for move in moves:
            self.move(move)
