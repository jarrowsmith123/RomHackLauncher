import os
from pathlib import Path
from config_manager import Config
from actions import delete_rom_action, install_patch_action, play_rom_action
from fetch import fetch_hack_list_from_server, download_image_from_server


class RomLauncherService:
    # Acts as API for the GUI
    def __init__(self):
        # Initialize dependencies
        self.config = Config()
        # For now storing raw dict for RomHacks
        self._available_hacks = {} # Stores data from hacks.json
        
        # Paths to external tools like patcher and emus could be like this:
        # self.emulator = Emulator(...) 
        # self.patcher = Patcher(...)  
        self._initialize_data()

    def _initialize_data(self):
        # Gets hack information and stores in _available_hacks
        hacks = fetch_hack_list_from_server(self.config) 
        if hacks:
            self._available_hacks = hacks
            print(f"Loaded {len(hacks)} hacks from server.")
        else:
            print("Failed to load hacks from server.")


    def update_settings(self, new_config_data):
        # Takes in a dict and saves this to the config - THIS WILL CHANGE MOST LIKELY
        self.config.save_config(new_config_data)
        # Re-initialize since the server url might become a setting in the future
        self._initialize_data() 
        return {'success': True, 'message': 'Settings updated successfully.'}

    def _get_installed_rom_ids(self):
        # Helper function to get path of all installed ROMs
        installed_files = set()
        patched_roms_dir = self.config.get_setting("patched_roms_dir")
        if patched_roms_dir and Path(patched_roms_dir).exists():
            try:
                # Iterate through files in the patched ROMs directory
                # I should probably make this a DB at some point or use something more sophisticated
                # Also need to add support for NDS in the future most likely
                for f in os.listdir(patched_roms_dir):
                    if f.lower().endswith(".gba"):
                        installed_files.add(Path(f).stem)
            except OSError as e:
                print(f"Error reading patched ROMs directory: {e}")
        return installed_files

    def get_installed_hacks(self):
        # Returns list of all installed ROMs with their information from the server
    
        installed_ids = self._get_installed_rom_ids()
        installed_hacks = []
        box_art_dir = Path(self.config.get_setting("box_art_dir"))
        patched_roms_dir = Path(self.config.get_setting("patched_roms_dir"))

        for hack_id, hack_info in self._available_hacks.items():
            if hack_id in installed_ids:
                # Construct the full path to the installed ROM
                patched_rom_path = patched_roms_dir / f"{hack_id}.gba"
                img_path = None
                if hack_info.get('box_art_url'):
                    img_path = box_art_dir / Path(hack_info.get('box_art_url')).name
                
                installed_hacks.append({
                    'id': hack_id,
                    'title': hack_info.get('name', hack_id),
                    'body': hack_info.get('description', 'No description available.'),
                    'img': str(img_path) if img_path and img_path.exists() else None,
                    'path': str(patched_rom_path),
                })
        return installed_hacks
    
    def get_available_hacks(self):
        # Returns the ROMs from the server not yet installed
        installed_ids = self._get_installed_rom_ids()
        available_hacks = []
        for hack_id, hack_info in self._available_hacks.items():
            if hack_id not in installed_ids:
                # We just pass the whole info dict through
                available_hacks.append(hack_info)
        return available_hacks

    def install_hack(self, hack_id):
        # Installs the patch and box art, and applies the patch
        # I will probably move some of the action logic back into this as its not so readable atm
        patch_info = self._available_hacks.get(hack_id)
        if not patch_info:
            return {'success': False, 'message': f"Hack with ID '{hack_id}' not found."}

        # Install boxart
        box_art_url = patch_info.get("box_art_url")
        if box_art_url:
            download_image_from_server(box_art_url, self.config)

        # Call the logic from actions.py, passing config
        result = install_patch_action(patch_info, self.config)
        
        return result

    def play_rom(self, rom_path):
        # Call the logic from actions.py, passing config
        # Again, I should move all the logic into app.py 
        return play_rom_action(rom_path, self.config)

    def delete_rom(self, rom_path):

        return delete_rom_action(rom_path)