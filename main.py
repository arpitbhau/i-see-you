# Jai Shree Ram

from utils.screen import start_screen_recording
from utils.cam import start_camera_recording
from utils.keylogger import start_keylogger
from utils.voice import start_voice_recording
import os
import keyboard
import sys
import threading
from datetime import datetime
import winsound


def add_audio_to_video(session_folder):
    cam_dir = os.path.join(session_folder, 'camera')
    voice_dir = os.path.join(session_folder, 'voice')
    output_dir = os.path.join(session_folder, 'final')
    os.makedirs(output_dir, exist_ok=True)
    
    # Get most recent recordings - updated prefixes
    cam_files = [f for f in os.listdir(cam_dir) if f.startswith('camera_')]
    voice_files = [f for f in os.listdir(voice_dir) if f.startswith('voice_')]
    
    if not cam_files or not voice_files:
        print("\nBoth camera and voice recordings are required!")
        return
        
    cam_file = os.path.join(cam_dir, sorted(cam_files)[-1])  # Get latest
    voice_file = os.path.join(voice_dir, sorted(voice_files)[-1])  # Get latest
    
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_file = os.path.join(output_dir, f'final_{timestamp}.avi')
    
    # Use ffmpeg to combine video with audio
    cmd = f'ffmpeg -i "{cam_file}" -i "{voice_file}" -c:v copy -c:a aac "{output_file}" -y'
    
    try:
        os.system(cmd)
        print(f"\nSuccessfully added audio to video: {output_file}")
        # Remove the original silent video and separate audio
        os.remove(cam_file)
        os.remove(voice_file)
        print("Original files cleaned up")
    except Exception as e:
        print(f"\nError processing files: {str(e)}")

def start_all_recordings():
    # Create session folder
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    session_folder = os.path.join('data', f'session_{timestamp}')
    
    # Create session directory and subdirectories
    for subfolder in ['screen', 'camera', 'voice', 'final', 'keylog']:
        os.makedirs(os.path.join(session_folder, subfolder), exist_ok=True)
    
    # Create threads for each recording function
    screen_thread = threading.Thread(target=lambda: globals().update(
        {'stop_screen': start_screen_recording(session_folder)}))
    cam_thread = threading.Thread(target=lambda: globals().update(
        {'stop_cam': start_camera_recording(session_folder)}))
    voice_thread = threading.Thread(target=lambda: globals().update(
        {'stop_voice': start_voice_recording(session_folder)}))
    keylogger_thread = threading.Thread(target=lambda: globals().update(
        {'stop_keylogger': start_keylogger(session_folder)}))
    
    # Start all threads simultaneously
    screen_thread.start()
    cam_thread.start()
    voice_thread.start()
    keylogger_thread.start()
    
    # Wait for all threads to complete initialization
    screen_thread.join()
    cam_thread.join()
    voice_thread.join()
    keylogger_thread.join()
    
    print(f"\nAll recordings started in session: {session_folder}")
    print("Press ESC to stop...")
    keyboard.wait('esc', suppress=True)
    
    # Stop all recordings
    globals()['stop_screen']()
    globals()['stop_cam']()
    globals()['stop_voice']()
    globals()['stop_keylogger']()
    print("\nAll recordings stopped!")
    
    # Combine audio and video
    add_audio_to_video(session_folder)

def view_recorded_data():
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("\nNo recordings found!")
        return
        
    print("\nRecorded files:")
    os.system("start ./data")
            
    input("\nPress Enter to continue...")

def print_control_room_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     ARPITBHAU's CONTROL ROOM                 ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  [1] Start All Recordings                                    ║
    ║  [2] View Recorded Data                                      ║
    ║  [ESC] Exit                                                  ║
    ║                                                              ║
    ║  All data will be saved in the 'data' directory              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def play_startup_sound():
    def play_sound():
        try:
            winsound.PlaySound("iseeu.wav", winsound.SND_FILENAME)
        except:
            print("Failed to play startup sound")  # Continue silently if sound fails to play
            
    sound_thread = threading.Thread(target=play_sound)
    sound_thread.daemon = True
    sound_thread.start()


def main():

    play_startup_sound()

    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        
    while True:
        print_control_room_banner()
        print("Select an option: ")

        try:
            # Wait for a single keypress
            event = keyboard.read_event(suppress=True)
            
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == '1':
                    start_all_recordings()
                elif event.name == '2':
                    view_recorded_data()
                elif event.name == 'esc':
                    print("\nExiting...")
                    sys.exit(0)
                    
            # Clear the screen for next iteration
            os.system('cls' if os.name == 'nt' else 'clear')
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()