import turtle
import math
import sys


def main():
    # Window setup
    screen = turtle.Screen()
    screen.setup(450, 450)
    screen.title("TurtleDraw")

    # Install close hook right away so clicking X always exits cleanly,
    # even during the filename prompt or any other dialog
    root = screen.getcanvas().winfo_toplevel()
    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))

    t = turtle.Turtle()
    t.speed(0)  # maximum speed

    # Prompt for filename, re-prompting on error
    infile = None
    prompt = "Enter the input file name:"
    while infile is None:
        filename = screen.textinput("Input file", prompt)
        if filename is None:
            # user cancelled the dialog
            return
        try:
            infile = open(filename, "r")
        except FileNotFoundError:
            prompt = f"File '{filename}' not found. Try again:"
        except OSError as e:
            prompt = f"Could not open file ({e.strerror}). Try again:"

    total_distance = 0.0
    prev_x, prev_y = None, None
    pen_down = False  # start with pen up so the first move doesn't draw from origin

    for line in infile:
        line = line.strip()
        if not line:
            continue

        parts = line.split()

        if parts[0] == "stop":
            t.penup()
            pen_down = False
            prev_x, prev_y = None, None
            continue

        color = parts[0]
        x = int(parts[1])
        y = int(parts[2])

        t.color(color)

        if not pen_down:
            # first point of a segment: move without drawing
            t.penup()
            t.goto(x, y)
            t.pendown()
            pen_down = True
        else:
            t.goto(x, y)
            # only count distance between connected points
            total_distance += math.hypot(x - prev_x, y - prev_y)

        prev_x, prev_y = x, y

    infile.close()

    # Print total distance toward bottom-right
    t.penup()
    t.color("black")
    t.goto(150, -200)
    t.write(f"Total distance: {total_distance:.2f}", align="right",
            font=("Arial", 10, "normal"))
    t.hideturtle()

    # Wait for Enter from either the terminal or the turtle window.
    # Run terminal input() in a background thread so the Tk main loop
    import threading

    done = threading.Event()

    def on_enter(event=None):
        done.set()

    root.bind("<Return>", on_enter)
    root.bind("<KP_Enter>", on_enter)  # numpad Enter
    root.focus_force()

    def wait_for_terminal():
        try:
            input("Press Enter (in terminal or turtle window) to close...")
        except (KeyboardInterrupt, EOFError):
            pass
        done.set()

    threading.Thread(target=wait_for_terminal, daemon=True).start()

    while not done.is_set():
        try:
            root.update()
        except Exception:
            # window was destroyed (X button): sys.exit already fired in the hook
            break

    try:
        screen.bye()
    except turtle.Terminator:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()
