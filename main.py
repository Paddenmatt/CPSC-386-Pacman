from run import GameController


def play():
    game = GameController()
    game.startGame()
    while True:
        if game.menu:
            game.main_menu()
        else:
            game.update()


if __name__ == "__main__":
    play()
