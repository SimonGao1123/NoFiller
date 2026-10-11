import tkinter as tk
import SpeechToText_v1

running = False

#First draft, might not use tkinter ltr on

def emit(msg):
    log.insert(tk.END, msg + "\n")
    log.see(tk.END)                 # auto-scroll to the newest line
    root.update()


def show_partial(text):
    partial_label.config(text=f"Partial: {text}")


def should_stop():
    root.update()                   # lets the window repaint and buttons respond
    return not running


def start():
    global running
    fillers = [f.strip().lower() for f in entry.get().split(",") if f.strip()]
    if not fillers:
        emit("Enter at least one filler word")
        return

    running = True
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")

    SpeechToText_v1.speech(fillers, emit=emit, on_partial=show_partial,
                           should_stop=should_stop)

    running = False
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    partial_label.config(text="")


def stop():
    global running
    running = False


root = tk.Tk()
root.title("Voice App")

tk.Label(root, text="Filler words (separate with commas):").pack()
entry = tk.Entry(root, width=40)
entry.insert(0, "like, you know, basically")
entry.pack()

start_btn = tk.Button(root, text="Start Listening", command=start)
start_btn.pack()
stop_btn = tk.Button(root, text="Stop", command=stop, state="disabled")
stop_btn.pack()

partial_label = tk.Label(root, text="")
partial_label.pack()

log = tk.Text(root, height=15, width=60)
log.pack()

root.mainloop()