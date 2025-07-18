import subprocess
import sys
import shutil

def apply_patch(patch_type, patcher_path, patch_file, input_file, output_file):
    # Calls the patcher with the correct command-line arguments to apply a patch
    if patch_type in ["bps","ips"]:
        # Flips (for .ips and .bps) uses this command structure
        cmd = [patcher_path, "--apply", patch_file, input_file, output_file]
    elif patch_type == "ups":
        # UPS Patcher uses this command structure
        cmd = [patcher_path, "apply", "--base", input_file, "--patch", patch_file, "--output", output_file]
    elif patch_type == "patch":
        # Correct command structure for applying an xdelta patch
        cmd = [patcher_path, "patch", patch_file, input_file, output_file]
    else:
        print(f"Unsupported patch type: {patch_type}")
        return False

    return execute_cli(cmd)

def execute_cli(cmd):
    try:
        # Run the patcher as a subprocess, hiding console output unless an error occurs
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        print(f"Patching successful! Patched file saved to: {cmd[-1]}")
        return True
    except FileNotFoundError:
        print(f"Error: Patcher executable not found at '{cmd[0]}'. Make sure it's in the application directory.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during patching: {e}")
        return False