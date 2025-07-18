import os
from pathlib import Path
from config_manager import Config

from fetch import fetch_hack_list_from_server
from rom import GBARom

# Acts as API for the GUI

class RomLauncherService:
    
    def __init__(self):
        self.config = Config()
        self._roms = {} # Stores GBARom objects, keyed by hack_id
        
        # Paths to external tools are handled within the GBARom class
        self._initialize_data()

    def _initialize_data(self):
        # Gets hack information from the server and populates the _roms dictionary
        hacks = fetch_hack_list_from_server(self.config) 
        if hacks:
            # Clear existing roms before populating
            self._roms.clear()
            for hack_id, hack_info in hacks.items():
                # For now, only GBA is supported. This can be expanded later
                if hack_info.get('system') == 'gba':
                    self._roms[hack_id] = GBARom(hack_info, self.config)

    def update_settings(self, new_config_data):
        # Saves new settings to the config file and re-initializes data
        self.config.save_config(new_config_data)
        self._initialize_data() 
        return {'success': True, 'message': 'Settings updated successfully.'}

    def get_installed_hacks(self, search_query=None, system=None, base_rom=None):
        # Returns a filtered list of all installed ROMs
        installed_hacks = [rom for rom in self._roms.values() if rom.is_installed]
        return self.filter_hacks(installed_hacks, search_query, system, base_rom)
    
    def get_available_hacks(self, search_query=None, system=None, base_rom=None):
        # Returns a filtered list of ROMs from the server that are not yet installed
        available_hacks = [rom for rom in self._roms.values() if not rom.is_installed]
        return self.filter_hacks(available_hacks, search_query, system, base_rom)

    def filter_hacks(self, rom_list, search_query=None, system=None, base_rom=None):
        # Applies search and filter criteria to a list of ROMs
        results = rom_list
        if search_query:
            results = [rom for rom in results if search_query.lower() in rom.name.lower()]
        if base_rom:
            results = [rom for rom in results if rom.base_rom_id == base_rom]
        if system:
            results = [rom for rom in results if rom.system == system]
        return results
    
    def install_hack(self, hack_id):
        # Triggers the download and patching process for a given hack
        rom_to_install = self._roms.get(hack_id)
        if not rom_to_install:
            return {'success': False, 'message': f"Hack with ID '{hack_id}' not found."}
        return rom_to_install.patch()

    def play_rom(self, rom_id):
        # Launches an installed ROM with the configured emulator
        rom_to_play = self._roms.get(rom_id)
        if rom_to_play:
            return rom_to_play.launch()
        return {'success': False, 'message': f"ROM with ID '{rom_id}' not found."}

    def delete_rom(self, rom_id):
        # Deletes an installed ROM file
        rom_to_delete = self._roms.get(rom_id)
        if rom_to_delete:
            return rom_to_delete.delete()
        return {'success': False, 'message': f"ROM with ID '{rom_id}' not found."}