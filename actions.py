import os
from pathlib import Path

from launch import launch_mgba_with_rom
from fetch import download_patch_from_server, download_image_from_server
from patch import apply_patch


# These actions are called by the buttons in the GUI
# They are kept here for easier testing and some better error handling because I am a pro at error handling


def delete_rom_action(rom_path):
    # Deletes the ROM hack if the user decides its dead
    # TODO maybe have an option to remove roms from the available list to clear it up? probably not

        try:
            os.remove(rom_path)
            print(f"Successfully deleted: {rom_path}")
            return {'success': True, 'message': f"Successfully deleted: {rom_path}"}
        except Exception as e:
            return {'success': False, 'message': f"Failed to delete ROM {rom_path}: {e}"}


def install_patch_action(patch_info, config):
    # Get all the important information from the dict
    base_rom = patch_info.get("base_rom_id")
    patch_url = patch_info.get("patch_file")
    patch_id = patch_info.get("id")
    
    # Pass config to download_patch_from_server
    patch_path = download_patch_from_server(patch_url, config)
    if not patch_path: # Check if download failed
        return {'success': False, 'message': "Failed to download patch file."}
        
    # Get base ROM path using config
    base_rom_path = config.get_setting("base_roms", {}).get(base_rom)
    if not base_rom_path:
        return {'success': False, 'message': f"Base ROM '{base_rom}' not configured."}

    patch_type = Path(patch_path).suffix[1:].lower()
    if patch_type == "ups":
        patcher_path = "ups.exe"
    else:
        patcher_path = "flips.exe"

    patched_roms_dir = config.get_setting("patched_roms_dir") # Get using config
    if not patched_roms_dir:
        return {'success': False, 'message': "Patched ROMs directory not configured."}
    
    # Ensure patched_roms_dir exists 
    Path(patched_roms_dir).mkdir(parents=True, exist_ok=True)

    patched_rom_path = Path(patched_roms_dir) / f"{patch_id}.gba"
    
    success = apply_patch(patch_type, patcher_path, patch_path, base_rom_path, str(patched_rom_path))

    # Remove patch file after
    try:
        os.remove(patch_path)
    except OSError as e:
        print(f"Warning: Could not remove patch file {patch_path}: {e}")

    if success:
        return {'success': True, 'message': f"Patch '{patch_info.get('name', patch_id)}' applied successfully!", 'patched_rom_path': str(patched_rom_path)}

    else:
        return {'success': False, 'message': "Patching failed."}
    
    

def play_rom_action(rom_path, config): 

    # This just launches the emulator with the chosen ROM

    emulator_path = config.get_setting("emulator_path") # Get using config
    if not emulator_path: 
        return {'success': False, 'message': f"Emulator not found!"}
    if not Path(rom_path).exists():
        return {'success': False, 'message': f"ROM Not Found!"}
    
    try:
        launch_mgba_with_rom(emulator_path, rom_path)
        return {'success': True, 'message': f"Launching {rom_path}..."}
    except FileNotFoundError as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        return {'success': False, 'message': f"Error playing ROM: {e}"}