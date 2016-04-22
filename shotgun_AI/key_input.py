"""getch waits for a single key input
 and the returns it without need for the enter key
 to be pressed mimicking the behavior of msvcrt.getwch() in
Windows"""

import sys
import tty
import termios

def getch():
    "
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

