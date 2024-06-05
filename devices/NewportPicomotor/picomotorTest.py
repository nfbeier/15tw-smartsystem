import numpy as np
from pylablib.devices import Newport
import sys

def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

def runMotor(stage,axis):
    run = True
    while run:
        char = getch().decode()

        print(stage.get_position())

        if char == "f":
            print("Forward")
            stage1.move_by(axis = axis, steps = 100)
            stage1.wait_move()

        if char == "r":
            print("Reverse")
            stage1.move_by(axis = axis, steps = -100)
            stage1.wait_move()

        if char == "s":
            run = False
            continue

        if char == "":
            continue

        # The keyboard character variable will be set to blank, ready
        # to save the next key that is pressed
        char = ""

        print(stage.get_position())

getch = _find_getch()

stage1 = Newport.Picomotor8742()

runMotor(stage1,1)

stage1.close()
