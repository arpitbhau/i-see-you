# Jai Shree Ram

import cv2
import numpy as np
import threading
import os
from datetime import datetime
import time
from PIL import ImageGrab

def start_screen_recording(session_folder):
    # Global control variables
    recording = False
    out = None

    def start_recording():
        nonlocal recording, out
        
        # Screen recording parameters
        screen = ImageGrab.grab()
        SCREEN_SIZE = screen.size
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = os.path.join(session_folder, 'screen', f'screen_{timestamp}.avi')
        
        # Create video writer object
        out = cv2.VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)
        
        recording = True
        print(f"Screen recording started: {filename}")

        try:
            while recording:
                frame = ImageGrab.grab()
                frame = np.array(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame)
                
        finally:
            if out:
                out.release()
                print(f"Screen recording saved to: {filename}")

    # Start recording in a separate thread
    record_thread = threading.Thread(target=start_recording)
    record_thread.daemon = True
    record_thread.start()
    
    return lambda: setattr(record_thread, 'recording', False)

# Example usage:
if __name__ == "__main__":
    stop_fn = start_screen_recording()
    
    # Let it record for 30 seconds as a test
    time.sleep(30)
    stop_fn()