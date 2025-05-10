import json
import os

# This is to save all the stuff to congig.JSON

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
        "leafgreen": "",
        "ruby": "",
        "sapphire": "",
        # Will potentially expand this later
    }
}

def load_config():

    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found. Creating default config at {CONFIG_FILE}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure all default keys exist, add them if missing from saved file
            updated = False
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                    updated = True
                # Ensure base_roms is a dict
                elif key == "base_roms" and not isinstance(config[key], dict):
                     config[key] = value # Reset if format is wrong
                     updated = True

            if updated:
                print("Config file updated with missing default keys.")
                save_config(config) # Save back the updated structure
            return config
    except Exception as e:
        print(f"Error loading config: {e}. Using default config.")
        save_config(DEFAULT_CONFIG) # Attempt to save a fresh default config
        return DEFAULT_CONFIG

def save_config(config_data):
    # Saves config to the JSON file

    # Ensure patched_roms_dir exists
    patched_dir = config_data.get("patched_roms_dir", DEFAULT_CONFIG["patched_roms_dir"])
    if patched_dir: # Only create if not empty
        os.makedirs(patched_dir, exist_ok=True)
    
    # Ensure patch_cache_dir exists
    patch_dir = config_data.get("patch_dir", DEFAULT_CONFIG["patch_dir"])
    if patch_dir:
        os.makedirs(patch_dir, exist_ok=True)

    # Ensure box_art_dir exists
    box_art_dir = config_data.get("box_art_dir", DEFAULT_CONFIG["box_art_dir"])
    if box_art_dir:
        os.makedirs(box_art_dir, exist_ok=True)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except IOError as e:
        print(f"Error saving config file {CONFIG_FILE}: {e}")

app_config = load_config()