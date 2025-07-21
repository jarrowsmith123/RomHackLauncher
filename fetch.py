import requests
import shutil
from pathlib import Path

# Create a single, reusable session object for all requests
# This enables connection pooling and is much more efficient
session = requests.Session()

def fetch_hack_list_from_server(config):
    # Gets the hacks.json file from the server
    server_url = config.get_setting("server_url")
    if not server_url:
        print("Error: Server URL not configured.")
        return None

    list_url = server_url.rstrip('/') + "/hacks.json" 

    try:
        # Use the shared session object for the request
        response = session.get(list_url, timeout=15) 
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hack list from {list_url}: {e}")
    except Exception as e: 
        print(f"An unexpected error occurred fetching hack list: {e}")
    return None


def download_patch_from_server(patch_url, config):
    # Downloads a patch file from the server if it doesn't exist locally
    patch_cache_dir = Path(config.get_setting("patch_dir", "downloaded_patches"))
    patch_cache_dir.mkdir(parents=True, exist_ok=True)

    local_patch_filename = Path(patch_url).name
    local_patch_path = patch_cache_dir / local_patch_filename

    if local_patch_path.exists():
        print(f"Patch already exists: {local_patch_path}")
        return str(local_patch_path)

    server_url = config.get_setting("server_url")
    if not server_url:
        print("Error: Server URL not configured. Cannot download patch.")
        return None

    download_url = server_url.rstrip('/') + '/' + patch_url.lstrip('/')
    print(f"Downloading patch: {download_url}")

    try:
        # Use the shared session object for the request
        response = session.get(download_url, timeout=30) # Increased timeout for larger files
        response.raise_for_status()
        with open(local_patch_path, "wb") as f:
            f.write(response.content)
        print(f"Patch downloaded to: {local_patch_path}")
        return str(local_patch_path)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading patch from {download_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred downloading patch to {local_patch_path}: {e}")
    return None


def download_image_from_server(image_url, config):
    # Downloads a box art image from the server if it doesn't exist locally
    image_cache_dir = Path(config.get_setting("box_art_dir", "box_art"))
    image_cache_dir.mkdir(parents=True, exist_ok=True)

    local_image_filename = Path(image_url).name
    local_image_path = image_cache_dir / local_image_filename

    # This check is crucial. If the art exists, we don't need to do anything
    if local_image_path.exists():
        return str(local_image_path)

    server_url = config.get_setting("server_url")
    if not server_url:
        print("Error: Server URL not configured. Cannot download image.")
        return None

    download_url = server_url.rstrip('/') + '/' + image_url.lstrip('/')
    print(f"Downloading image: {download_url}")

    try:
        # Use the shared session and stream the response for efficiency
        response = session.get(download_url, stream=True, timeout=15)
        response.raise_for_status()
        with open(local_image_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        # We don't print success here to avoid cluttering the console during bulk downloads
        return str(local_image_path)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {download_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred downloading image to {local_image_path}: {e}")
    return None