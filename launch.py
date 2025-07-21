
import subprocess
import os

def launch_mgba_with_rom(emulator_path, rom_path):
    if not os.path.exists(emulator_path):
        raise FileNotFoundError(f"mGBA executable not found at: {emulator_path}")
    
    if not os.path.exists(rom_path):
        raise FileNotFoundError(f"ROM file not found at: {rom_path}")
    
    try:
        subprocess.Popen([emulator_path, rom_path])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching mGBA: {e}")
        return False

