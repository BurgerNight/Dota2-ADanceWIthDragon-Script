import time
import json
from pynput import mouse, keyboard
from datetime import datetime

recording = []


def on_press(key):
    try:
        json_object = {
            'action': 'pressed_key',
            'key': key.char,
            '_time': time.time()
        }
    except AttributeError:
        if key == keyboard.Key.esc:
            print("Recording ended.")
            return False

        json_object = {
            'action': 'pressed_key',
            'key': str(key),
            '_time': time.time()
        }

    recording.append(json_object)


def on_release(key):
    try:
        json_object = {
            'action': 'released_key',
            'key': key.char,
            '_time': time.time()
        }
    except AttributeError:
        json_object = {
            'action': 'released_key',
            'key': str(key),
            '_time': time.time()
        }

    recording.append(json_object)


def on_move(x, y):
    if len(recording) >= 1:
        if (recording[-1]['action'] == "pressed" and recording[-1]['button'] == 'Button.left') or (
                recording[-1]['action'] == "moved" and time.time() - recording[-1]['_time'] > 0.02):
            json_object = {
                'action': 'moved',
                'x': x,
                'y': y,
                '_time': time.time()
            }

            recording.append(json_object)


def on_click(x, y, button, pressed):
    json_object = {
        'action': 'clicked' if pressed else 'unclicked',
        'button': str(button),
        'x': x,
        'y': y,
        '_time': time.time()
    }

    recording.append(json_object)


def on_scroll(x, y, dx, dy):
    json_object = {
        'action': 'scroll',
        'vertical_direction': int(dy),
        'horizontal_direction': int(dx),
        'x': x,
        'y': y,
        '_time': time.time()
    }

    recording.append(json_object)


def start_recording():
    print("Press 'ESC' to end the recording.")

    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    mouse_listener = mouse.Listener(
        on_click=on_click,
        on_scroll=on_scroll,
        on_move=on_move)

    keyboard_listener.start()
    mouse_listener.start()
    keyboard_listener.join()
    mouse_listener.stop()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(recording, f)
    print("Recording saved to {}".format(filename))


if __name__ == "__main__":
    time.sleep(5)
    start_recording()
