# Jai Shree Ram

import pyaudio
import wave
import threading
import os
from datetime import datetime
import time

def start_voice_recording(session_folder):
    # Global control variables
    recording = False
    audio = None
    stream = None
    frames = []
    current_filename = None

    def start_recording():
        nonlocal recording, audio, stream, frames, current_filename
        
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        current_filename = os.path.join(session_folder, 'voice', f'voice_{timestamp}.wav')
        
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
        
        recording = True
        frames = []
        print(f"Voice recording started: {current_filename}")
        
        start_time = time.time()
        
        try:
            while recording:
                data = stream.read(CHUNK)
                frames.append(data)
                
                # Save recording every 10 seconds
                current_time = time.time()
                if current_time - start_time >= 10:
                    save_audio(current_filename, frames, audio, FORMAT, CHANNELS, RATE)
                    print(f"Saved 10 seconds of audio")
                    frames = []
                    start_time = current_time
            
            # Save any remaining audio
            if frames:
                save_audio(current_filename, frames, audio, FORMAT, CHANNELS, RATE)
                print(f"Final audio segment saved")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            if audio:
                audio.terminate()
            print(f"Voice recording saved to: {current_filename}")

    def save_audio(filename, frames, audio, FORMAT, CHANNELS, RATE):
        if os.path.exists(filename):
            with wave.open(filename, 'rb') as wf:
                existing_frames = wf.readframes(wf.getnframes())
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(existing_frames)
                wf.writeframes(b''.join(frames))
        else:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

    # Start recording in a separate thread
    record_thread = threading.Thread(target=start_recording)
    record_thread.daemon = True  # Make thread daemon so it exits when main program exits
    record_thread.start()
    
    def stop_recording():
        nonlocal recording
        recording = False
        record_thread.join(timeout=5)  # Wait for thread to finish with timeout
        
    return stop_recording
