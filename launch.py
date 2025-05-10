
import subprocess
import os

def launch_mgba_with_rom(mgba_path, rom_path):
    if not os.path.exists(mgba_path):
        raise FileNotFoundError(f"mGBA executable not found at: {mgba_path}")
    
    if not os.path.exists(rom_path):
        raise FileNotFoundError(f"ROM file not found at: {rom_path}")
    
    try:
        subprocess.run([mgba_path, rom_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching mGBA: {e}")
        return False

