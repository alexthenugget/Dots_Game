import sys
from tkinter import PhotoImage, Tk

from constants import HEIGHT, WIDTH
from dots_game import DotsGame


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == 'help':
        from help import print_help

        print_help()
        return

    root: Tk = Tk()
    root.title("Dots Game")
    icon: PhotoImage = PhotoImage(file="ikon.png")
    root.iconphoto(True, icon)
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(width=False, height=False)
    game: DotsGame = DotsGame(root)
    game.start()
    root.mainloop()


if __name__ == "__main__":
    main()
