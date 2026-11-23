import sys
import random

import poker
import numberguessing
import highlowcardbettinggame

OPTIONS = [
    ("Play Poker: ", poker.start),
    ("Play Number Guessing Game: ", numberguessing.start),
    ("Play High-Lo: ", highlowcardbettinggame.start),
    ("Exit: ", None),
]
def clear_screen():
    print("\033[2J\033[H", end=", flush=True") #ansi code; it clears the screen 

def get_key():
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):          
            return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "")
        if ch == "\r":
            return "enter"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":                
                if sys.stdin.read(1) == "[":
                    return {"A": "up", "B": "down"}.get(sys.stdin.read(1), "")
                return ""
            if ch in ("\r", "\n"):
                return "enter"
            if ch == "\x03":
                raise KeyboardInterrupt
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def draw_menu(selected):
    clear_screen()
    print("\033[1;36m========= Main Menu =========\033[0m\n")
    for i, (label, _) in enumerate(OPTIONS):
        if i == selected:
            print("  \033[7m > " + label + " \033[0m")
        else:
            print("    " + label)
    print("\n  Use \u2191/\u2193 to move, Enter to select")


def arrow_menu():
    selected = 0
    while True:
        draw_menu(selected)
        key = get_key()
        if key in ("up", "w", "k"):
            selected = (selected - 1) % len(OPTIONS)
        elif key in ("down", "s", "j"):
            selected = (selected + 1) % len(OPTIONS)
        elif key.isdigit() and 1 <= int(key) <= len(OPTIONS):
            return int(key) - 1            
        elif key == "enter":
            return selected


def text_menu():
    while True:
        print("\n========= Main Menu =========")
        for i, (label, _) in enumerate(OPTIONS):
            print(str(i + 1) + ". " + label)
        choice = input("Choose (1-" + str(len(OPTIONS)) + "): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(OPTIONS):
            return int(choice) - 1
        print("Invalid choice")


def main():
    try:
        while True:
            index = arrow_menu() if sys.stdin.isatty() else text_menu()
            label, action = OPTIONS[index]

            clear_screen()
            if action is None:
                break
            action()
            input("\nPress Enter to return to the menu...")
    except KeyboardInterrupt:
        print()
    print("Thanks for playing")


if __name__ == "__main__":
    main()


