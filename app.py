import os
from pathlib import Path
from config_manager import Config

from fetch import fetch_hack_list_from_server, download_image_from_server
from rom import GBARom

class RomLauncherService:
    # Acts as API for the GUI
    def __init__(self):
        # Initialize dependencies
        self.config = Config()
        # For now storing raw dict for RomHacks
        self._roms = {} # Stores data from hacks.json
        
        # Paths to external tools like patcher and emus could be like this:
        # self.emulator = Emulator(...) 
        # self.patcher = Patcher(...)  
        self._initialize_data()

    def _initialize_data(self):
        # Gets hack information and stores in _roms
        hacks = fetch_hack_list_from_server(self.config) 
        if hacks:
            for hack_id, hack_info in hacks.items():
            # This is a simple factory based on a new 'system' key in hacks.json
                if hack_info.get('system') == 'gba':
                    self._roms[hack_id] = GBARom(hack_info, self.config)


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

    def get_installed_hacks(self, search_query=None,system=None,base_rom=None):
        # Returns list of all installed ROMs with their information from the server
        installed_hacks = [rom for rom in self._roms.values() if rom.is_installed]
        return self.filter_hacks(installed_hacks, search_query, system, base_rom)
    
    def get_available_hacks(self, search_query=None,system=None,base_rom=None):
        # Returns the ROMs from the server not yet installed
        available_hacks = [rom for rom in self._roms.values() if not rom.is_installed]
        return self.filter_hacks(available_hacks, search_query, system, base_rom)


    def filter_hacks(self, rom_list, search_query=None, system=None, base_rom=None):

        results = rom_list
        if search_query:
            results = [rom for rom in results if search_query.lower() in rom.name.lower()]
        if base_rom:
            results = [rom for rom in results if rom.base_rom_id == base_rom]
        if system:
            results = [rom for rom in results if rom.system == system]

        return results
    
    def install_hack(self, hack_id):
        # Installs the patch and box art, and applies the patch
        # I will probably move some of the action logic back into this as its not so readable atm
        rom_to_install = self._roms.get(hack_id)
        if not rom_to_install:
            return {'success': False, 'message': f"Hack with ID '{hack_id}' not found."}

        # Install boxart
        if rom_to_install.box_art_url:
            download_image_from_server(rom_to_install.box_art_url, self.config)

        return rom_to_install.patch()


    def play_rom(self, rom_id):
        rom_to_play = self._roms.get(rom_id)
        if rom_to_play:
            return rom_to_play.launch()
        return {'success': False, 'message': f"ROM not found"}

    def delete_rom(self, rom_id):
        rom_to_delete = self._roms.get(rom_id)
        if rom_to_delete:
            return rom_to_delete.delete()
        return {'success': False, 'message': f"ROM not found"}