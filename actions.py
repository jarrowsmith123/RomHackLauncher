import os
from pathlib import Path
from tkinter import messagebox
from launch import launch_mgba_with_rom
from fetch import download_patch_from_server, download_image_from_server
from patch import apply_patch


# These actions are called by the buttons in the GUI
# They are kept here for easier testing and some better error handling because I am a pro at error handling


def delete_rom_action(rom_title, rom_path, item_frame_widget, window):
    # Deletes the ROM hack if the user decides its dead
    # TODO maybe have an option to remove roms from the available list to clear it up? probably not

    # Make sure to double check with a message box
    confirmed = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{rom_title}'?\n({rom_path})", icon='warning', parent=window)
    if confirmed:
        try:
            os.remove(rom_path)
            print(f"Successfully deleted: {rom_path}")
            item_frame_widget.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {e}", parent=window)


def install_patch_action(patch_info, window, app_config):

    # Get all the important information from the dict
    base_rom = patch_info.get("base_rom_id")
    patch_url = patch_info.get("patch_file")
    patch_id = patch_info.get("id")
    patch_path = download_patch_from_server(patch_url)

    if not patch_path: # Check if download failed
        messagebox.showerror("Error", f"Failed to download patch: {patch_url}", parent=window)
        return
        
    download_image_from_server(patch_info.get("box_art_url"))
    # Is this how you get the key again? I honestly not sure but I found this on a stackoverflow thread and it works
    base_rom_path = app_config.get("base_roms", {}).get(base_rom)

    if not base_rom_path or not Path(base_rom_path).exists():
        messagebox.showerror("Error", f"Base ROM '{base_rom}' not found or path not configured.", parent=window)
        return

    # TODO make the patcher path configurable
    patch_type = Path(patch_path).suffix[1:].lower()
    if patch_type == "ups":
        patcher_path = "ups.exe"
    else:
        patcher_path = "flips.exe"

    patched_roms_dir = app_config.get("patched_roms_dir")
    if not patched_roms_dir:
        messagebox.showerror("Error", "Patched ROMs directory not set in Settings.", parent=window)
        return
    
    # Ensure patched_roms_dir exists 
    # !! I think I already do this in another file but I might as well leave it in because I have done enough testing
    Path(patched_roms_dir).mkdir(parents=True, exist_ok=True)

    patched_rom_path = Path(patched_roms_dir) / f"{patch_id}.gba"
    
    success = apply_patch(patch_type, patcher_path, patch_path, base_rom_path, str(patched_rom_path))
    if success:
        messagebox.showinfo("Success", f"Patch '{patch_info.get('name', patch_id)}' applied successfully!", parent=window)

    else:
        messagebox.showerror("Patching Failed", parent=window)
    
    # Remove patch file after
    try:
        os.remove(patch_path)
    except OSError as e:
        print(f"Warning: Could not remove patch file {patch_path}: {e}")


def play_rom_action(rom_path, window, app_config):

    # This just launches the emulator with the chosen ROM

    emulator_path = app_config.get("emulator_path")
    if not emulator_path:
        messagebox.showerror("Emulator Not Found", "Emulator path is not set. Please configure it in Settings.", parent=window)
        return
    if not Path(rom_path).exists():
        messagebox.showerror("ROM Not Found", f"ROM file not found at the specified path:\n{rom_path}", parent=window)
        return
    success = launch_mgba_with_rom(emulator_path, rom_path)
    if not success:
        messagebox.showerror("Launch Error", f"Failed to launch Emulator", parent=window)
