# Jai Shree Ram
import cv2
from pynput import keyboard
import threading
import os
from datetime import datetime
import time
from utils.common import get_session_folder

def start_camera_recording(session_folder):
    # Global control variables
    recording = False
    camera = None
    out = None
    last_save_time = 0

    def start_recording():
        nonlocal recording, camera, out, last_save_time
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = os.path.join(session_folder, 'camera', f'camera_{timestamp}.avi')
        
        camera = cv2.VideoCapture(0)
        frame_width = int(camera.get(3))
        frame_height = int(camera.get(4))
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))
        print(f"Started camera recording: {filename}")
        
        recording = True
        last_save_time = time.time()
        
        try:
            while recording:
                ret, frame = camera.read()
                if ret:
                    out.write(frame)
                    cv2.imshow('Recording... (Press ESC to stop)', frame)
                    
                    current_time = time.time()
                    if current_time - last_save_time >= 10:
                        print(f"Saved 10 seconds of video")
                        last_save_time = current_time
                    
                    if cv2.waitKey(1) & 0xFF == 27:
                        recording = False
                        break
        finally:
            if out is not None:
                out.release()
            if camera is not None:
                camera.release()
            cv2.destroyAllWindows()
            print(f"Camera recording saved to: {filename}")

    def on_press(key):
        nonlocal recording
        try:
            if key == keyboard.Key.esc:  # Press ESC to stop recording
                recording = False
                print("Recording stopped!")
        except AttributeError:
            pass

    def on_release(key):
        pass

    # Start keyboard listener
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    # Start recording in a separate thread
    record_thread = threading.Thread(target=start_recording)
    record_thread.daemon = True  # Make thread daemon so it exits when main program exits
    record_thread.start()
    
    return lambda: setattr(record_thread, 'recording', False)

# This code should not be in utils/cam.py
# It appears to be misplaced code that belongs in main.py
# The camera module should only contain the camera recording functionality
