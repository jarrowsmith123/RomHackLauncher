import json
import os
from pathlib import Path
# This is to save all the stuff to congig.JSON
# Main to-do is to move away from the dict approach I started with
# ConfigManager should probably just be Config and have an attribute for each value
# Same with ROMs - why didnt i just start with OOP i hate scope creep

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

        if not os.path.exists(self.config_file):
            print(f"Config file not found. Creating default config at {self.config_file}")
            self.config_data = self.default_config.copy()
            self.save_config()
            return

        try:
            with open(self.config_file, 'r') as f:
                # Load data directly into the instance's config_data attribute
                self.config_data = json.load(f)

            # Validate the loaded config against default
            updated = False
            for key, value in self.default_config.items():
                if key not in self.config_data:
                    self.config_data[key] = value
                    updated = True
                # Ensure nested dicts like base_roms exist
                elif key == "base_roms" and not isinstance(self.config_data.get(key), dict):
                    self.config_data[key] = value
                    updated = True
            
            if updated:
                print("Config file updated with missing default keys.")
                # Save_config will use the updated self.config_data
                self.save_config() 
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file '{self.config_file}': {e}. Using default config.")
            self.config_data = self.default_config.copy()
            self.save_config() # Attempt to save a fresh default config

    def get_setting(self, key, default=None):
        # Get method for a particular value in the config
        # This nested get allows accessing keys like "base_roms"
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set_setting(self, key, value):
        # Set method for particular config value
        self.config_data[key] = value

    def save_config(self, new_config = None):
        # Saves config to the JSON file

        if new_config:
            self.config_data.update(new_config)
        # Ensure all dirs exists
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

