# Jai Shree Ram
from datetime import datetime
import os

def get_session_folder():
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    base_folder = f'data/session_{timestamp}'
    
    # Create main session folder and subfolders
    for subfolder in ['screen', 'camera', 'voice']:
        folder_path = os.path.join(base_folder, subfolder)
        os.makedirs(folder_path, exist_ok=True)
    
    return base_folder 