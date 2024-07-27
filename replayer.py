import json
from pynput.keyboard import Controller as KeyboardController, Key, Listener
from pynput.mouse import Controller as MouseController, Button
import time

keyboard = KeyboardController()
mouse = MouseController()
start_replay = False
stop_replay = False

# Add more key mappings if needed
key_mappings = {
    "cmd": Key.cmd,
    "alt_l": Key.alt_l,
    "alt_r": Key.alt_r,
    "ctrl_l": Key.ctrl_l,
    "ctrl_r": Key.ctrl_r,
    "esc": Key.esc,
    "tab": Key.tab,
    "shift": Key.shift,
    "space": Key.space,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
}


def read_json_file(filename='recording.json'):
    try:
        with open(filename) as f:
            recording = json.load(f)
        return recording
    except FileNotFoundError:
        print("File `{}` does not exist. Make sure the recording file is in the current directory.".format(filename))
        time.sleep(5)
        exit(0)


def on_press(key):
    global start_replay
    global stop_replay
    try:
        if key.char == 'b':
            start_replay = True
    except AttributeError:
        if key == Key.esc:
            stop_replay = True
            return False


def replay(recording):
    if not recording:
        return

    global stop_replay
    global start_replay

    while not start_replay:
        time.sleep(1)

    record_start_time = recording[0]["_time"]
    real_start_time = time.time()
    cumulative_extra_time = 0

    for i, step in enumerate(recording):
        if stop_replay:
            mouse.release(Button.left)
            mouse.release(Button.right)
            keyboard.release("w")
            keyboard.release("a")
            keyboard.release("s")
            keyboard.release("d")
            print("Replay stopped by user.")
            break

        print(i, step)
        print('=' * 50)

        if i > 0:
            prev = i - 1
            record_total_time_cost = recording[prev]["_time"] - record_start_time
            real_total_time_cost = time.time() - real_start_time
            cumulative_extra_time += real_total_time_cost - record_total_time_cost

            pause_in_seconds = step["_time"] - recording[prev]["_time"]
            adjusted_pause_in_seconds = pause_in_seconds - cumulative_extra_time

            if adjusted_pause_in_seconds >= 0:
                time.sleep(adjusted_pause_in_seconds)
                cumulative_extra_time = 0
            else:
                cumulative_extra_time = -adjusted_pause_in_seconds

        if step["action"] == "pressed_key":
            key = step["key"].replace("Key.", "") if "Key." in step["key"] else step["key"]
            key = key_mappings.get(key, key)  # Use Key object for special keys
            keyboard.press(key)

        elif step["action"] == "released_key":
            key = step["key"].replace("Key.", "") if "Key." in step["key"] else step["key"]
            key = key_mappings.get(key, key)  # Use Key object for special keys
            keyboard.release(key)

        elif step["action"] == "clicked":
            button = Button.right if step["button"] == "Button.right" else Button.left
            mouse.press(button)

        elif step["action"] == "unclicked":
            button = Button.right if step["button"] == "Button.right" else Button.left
            mouse.release(button)

    print('Replay ended')


if __name__ == "__main__":
    recording = read_json_file()
    print("Please move your mouse over the play button, then press 'b' to start.")
    print("Press 'esc' to end the replay.")
    listener = Listener(on_press=on_press)
    listener.start()
    replay(recording)
