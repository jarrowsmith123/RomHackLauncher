import subprocess
import sys
import shutil


def apply_patch(patch_type, patcher_path, patch_file, input_file, output_file):
    # Calls the patcher with subprocess to apply the patch
    
    print(patch_type, patcher_path, patch_file, input_file, output_file)
    # make a copy of the input file first
    try:
        shutil.copy2(input_file, output_file)
    except Exception as e:
        print(f"Error creating output file: {e}")
        return False

    if patch_type in ["bps","ips"]:
        if sys.platform == "win32":
            cmd = [patcher_path, "--apply", patch_file, input_file, output_file]
    else:
        cmd = [patcher_path, "apply", "--base", input_file, "--patch", patch_file, "--output", output_file]

    return execute_cli(cmd)

def execute_cli(cmd):
    try:
        # run the patcher with subprocess
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Patching successful! Patched file saved to: {cmd[-1]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during patching: {e}")
        return False
        
