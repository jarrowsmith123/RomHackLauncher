import json
import os
from pathlib import Path

# Manages loading and saving application settings from config.json
class Config:

    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG = {
        "emulator_path": "",
        "server_url": "https://jarrowsmith123.github.io/RomHack-Launcher-Assets/",
        "patch_dir": "downloaded_patches",
        "box_art_dir": "box_art",
        "patched_roms_dir": "patched_roms",
        "base_roms": {
            "firered": "",
            "emerald": "",
        }
    }

    def __init__(self, config_file=CONFIG_FILE, default_config=DEFAULT_CONFIG):
        self.config_file = config_file
        self.default_config = default_config
        self.config_data = {} 
        self.load_config()

    def load_config(self):
        # Creates a default config file if one doesn't exist
        if not os.path.exists(self.config_file):
            print(f"Config file not found. Creating default config at {self.config_file}")
            self.config_data = self.default_config.copy()
            self.save_config()
            return

        try:
            with open(self.config_file, 'r') as f:
                self.config_data = json.load(f)

            # Validate the loaded config, adding any missing default keys
            updated = False
            for key, value in self.default_config.items():
                if key not in self.config_data:
                    self.config_data[key] = value
                    updated = True
                # Ensure nested dicts like base_roms are correctly typed
                elif key == "base_roms" and not isinstance(self.config_data.get(key), dict):
                    self.config_data[key] = value
                    updated = True
            
            if updated:
                print("Config file updated with missing default keys.")
                self.save_config() 
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file '{self.config_file}': {e}. Using default config.")
            self.config_data = self.default_config.copy()
            self.save_config()

    def get_setting(self, key, default=None):
        # Retrieves a setting value by its key
        return self.config_data.get(key, default)
    
    def set_setting(self, key, value):
        # Updates a setting value in memory
        self.config_data[key] = value

    def save_config(self, new_config=None):
        # Saves the current configuration to the JSON file
        if new_config:
            self.config_data.update(new_config)
            
        # Ensure all required directories exist
        for key in ["patched_roms_dir", "patch_dir", "box_art_dir"]:
            dir_path = self.config_data.get(key)
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving config file {self.config_file}: {e}")