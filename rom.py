# rom.py
import abc
from pathlib import Path
from patch import apply_patch
from launch import launch_mgba_with_rom
from fetch import download_patch_from_server


class ROM(abc.ABC):
    def __init__(self, hack_info: dict, config):
        # Store the raw data and the config object
        self.raw_data = hack_info
        self.config = config

        # Attributes from hacks.JSON 
        self.id = hack_info.get('id')
        self.name = hack_info.get('name')
        self.description = hack_info.get('description')
        self.base_rom_id = hack_info.get('base_rom_id')
        self.box_art_url = hack_info.get('box_art_url')
        self.patch_file_url = hack_info.get('patch_file')
        self.author = hack_info.get('author')

    @property
    def patched_rom_path(self) -> Path:
        # Returns the expected path of the final, patched ROM file
        patched_dir = Path(self.config.get_setting("patched_roms_dir"))
        # The extension will need to change for nds etc in future
        return patched_dir / f"{self.id}.gba" 

    @property
    def is_installed(self) -> bool:
        """Checks if the patched ROM file exists."""
        return self.patched_rom_path.exists()

    @abc.abstractmethod
    def patch(self):
        # Abstract method for patching, all ROM subclasses must override this
        raise NotImplementedError

    @abc.abstractmethod
    def launch(self):
        # Abstract method for launching, different ROMs use different emulators
        raise NotImplementedError

    def delete(self):
        # Deletes the patched ROM file. This will be the same for all ROM types
        try:
            if self.is_installed:
                self.patched_rom_path.unlink()
                return {'success': True, 'message': f"Deleted {self.name}."}
            return {'success': False, 'message': "ROM not found, nothing to delete."}
        except OSError as e:
            return {'success': False, 'message': f"Error deleting {self.name}: {e}"}
        

class GBARom(ROM):
    def patch(self):

        # Get necessary paths from config
        base_rom_path_str = self.config.get_setting("base_roms", {}).get(self.base_rom_id)
        if not base_rom_path_str or not Path(base_rom_path_str).exists():
            return {'success': False, 'message': f"Base ROM '{self.base_rom_id}' not found or configured."}

        # Download the patch file
        patch_path_str = download_patch_from_server(self.patch_file_url, self.config)
        if not patch_path_str:
            return {'success': False, 'message': 'Failed to download patch file.'}
        
        # TODO I should make the patch type an attribute for the hack.json
        # Determine correct patcher and apply
        patch_path = Path(patch_path_str)
        patch_type = patch_path.suffix[1:].lower()
        patcher_path = "ups.exe" if patch_type == "ups" else "flips.exe"
        
        success = apply_patch(
            patch_type,
            patcher_path,
            str(patch_path),
            base_rom_path_str,
            str(self.patched_rom_path)
        )
        
        # Remove patch file after using
        patch_path.unlink() 
        
        if success:
            return {'success': True, 'message': f"'{self.name}' installed successfully!"}
        else:
            return {'success': False, 'message': f"Patching for '{self.name}' failed."}

    def launch(self):
        # TODO more emu support
        emulator_path = self.config.get_setting("emulator_path")
        if not emulator_path:
            return {'success': False, 'message': "Emulator path not set in settings."}
        
        if not self.is_installed:
            return {'success': False, 'message': f"ROM for {self.name} is not installed."}

        try:
            launch_mgba_with_rom(emulator_path, str(self.patched_rom_path))
            return {'success': True, 'message': f"Launching {self.name}..."}
        except Exception as e:
            return {'success': False, 'message': f"Error launching ROM: {e}"}
        
