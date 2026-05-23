from game_logic import GameLogic

game = GameLogic(3)
print(game.board)
print(game.empty_pos)

game.randomize()

while(not game.is_solved()):
    game.randomize(1)
    print(game.board)
    print(game.empty_pos)
