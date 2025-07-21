import abc
from pathlib import Path
import os
from patch import apply_patch
from launch import launch_mgba_with_rom
from fetch import download_patch_from_server

class ROM(abc.ABC):
    def __init__(self, hack_info, config):
        # Store the raw data from hacks.json and the config object
        self.raw_data = hack_info
        self.config = config

        # Core attributes from the hack's data
        self.id = hack_info.get("id")
        self.name = hack_info.get("name")
        self.description = hack_info.get("description")
        self.base_rom_id = hack_info.get("base_rom_id")
        self.box_art_url = hack_info.get("box_art_url")
        self.patch_file_url = hack_info.get("patch_file")
        self.author = hack_info.get("author")
        self.system = hack_info.get("system")
        

    @property
    def patched_rom_path(self) -> Path:
        # Returns the expected path of the final, patched ROM file.
        patched_dir = Path(self.config.get_setting("patched_roms_dir"))
        return patched_dir / f"{self.id}.{self.system}" 

    @abc.abstractmethod
    def patch(self):
        # Abstract method for patching. Subclasses must implement this.
        raise NotImplementedError

    @abc.abstractmethod
    def launch(self):
        # Abstract method for launching. Subclasses must implement this.
        raise NotImplementedError

    def delete(self):
        # Deletes the patched ROM file. This logic is shared across ROM types.
        try:
            if self.patched_rom_path.exists():
                self.patched_rom_path.unlink()
                print(f"Deleted {self.name}.")
                return True
            print("ROM not found, nothing to delete.")
            return False
        except OSError as e:
            print(f"Error deleting {self.name}: {e}")
            return False
        
# TODO I think there is more common logic across system types.
class GBARom(ROM):
    def patch(self):
        # Handles the patching process for a GBA ROM.
        base_roms = self.config.get_setting("base_roms", {})
        base_rom_path_str = base_roms.get(self.base_rom_id)
        if not base_rom_path_str or not Path(base_rom_path_str).exists():
            print(f"Base ROM '{self.base_rom_id}' not found or configured.")
            return False

        # Download the patch file from the server.
        patch_path_str = download_patch_from_server(self.patch_file_url, self.config)
        if not patch_path_str:
            print("Failed to download patch fie")
            return False
        
        # Determine patch type and required patcher executable from the file extension.
        patch_path = Path(patch_path_str)
        patch_type = patch_path.suffix[1:].lower()
        
        # Flips handles both .ips and .bps
        patcher_path = "ups.exe" if patch_type == "ups" else "flips.exe"
        
        success = apply_patch(
            patch_type,
            patcher_path,
            str(patch_path),
            base_rom_path_str,
            str(self.patched_rom_path)
        )
        
        # Clean up by removing the downloaded patch file after use.
        try:
            patch_path.unlink()
        except OSError as e:
            print(f"Warning: Could not remove patch file {patch_path}: {e}")

        if success:
            print(f"'{self.name}' installed successfully!")
            return True
        else:
            # If patching failed, clean up the invalid output file that may have been created.
            if self.patched_rom_path.exists():
                self.patched_rom_path.unlink()
            print(f"Patching for '{self.name}' failed.")
            return False
            

    def launch(self):
        # Launches the installed GBA ROM using the configured emulator.
        emulator_path = self.config.get_setting("gba_emulator_path")
        if not emulator_path or not os.path.exists(emulator_path):
            print("Emulator path not set or invalid")
            return False
        
        if not self.patched_rom_path.exists():
            print(f"{self.name} ROM is not installed.")
            return True

        try:
            launch_mgba_with_rom(emulator_path, str(self.patched_rom_path))
            print(f"Launching {self.name}...")
            return True
        except Exception as e:
            print(f"Error launching ROM: {e}")
            return False
        

class NDSRom(ROM):
    def patch(self):
        # Handles the patching process for a GBA ROM.
        base_roms = self.config.get_setting("base_roms", {})
        base_rom_path_str = base_roms.get(self.base_rom_id)
        if not base_rom_path_str or not Path(base_rom_path_str).exists():
            print(f"Base ROM '{self.base_rom_id}' not found or configured.")
            return False

        # Download the patch file from the server.
        patch_path_str = download_patch_from_server(self.patch_file_url, self.config)
        if not patch_path_str:
            print("Failed to download patch file.")
            return False
        
        # Determine patch type and required patcher executable from the file extension.
        patch_path = Path(patch_path_str)
        patch_type = patch_path.suffix[1:].lower()
        
        patcher_path = "xdelta.exe"
        
        success = apply_patch(
            patch_type,
            patcher_path,
            str(patch_path),
            base_rom_path_str,
            str(self.patched_rom_path)
        )
        
        # Clean up by removing the downloaded patch file after use.
        try:
            patch_path.unlink()
        except OSError as e:
            print(f"Warning: Could not remove patch file {patch_path}: {e}")

        if success:
            print(f"'{self.name}' installed successfully!")
            return True
        else:
            # If patching failed, clean up the invalid output file that may have been created.
            if self.patched_rom_path.exists():
                self.patched_rom_path.unlink()
            print(f"Patching for '{self.name}' failed.")
            return False

    def launch(self):
        # Launches the installed GBA ROM using the configured emulator.
        emulator_path = "melonDS.exe"
        if not emulator_path or not os.path.exists(emulator_path):
            print("Emulator path is not set or is invalid.")
            return False
        
        if not self.patched_rom_path.exists():
            print(f"ROM for {self.name} is not installed.")
            return False

        try:
            launch_mgba_with_rom(emulator_path, str(self.patched_rom_path))
            print(f"Launching {self.name}...")
            return True
        except Exception as e:
            print(f"Error launching ROM: {e}")
            return False