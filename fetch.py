
import requests
import shutil
from pathlib import Path


def fetch_hack_list_from_server(config):
    # Essentially gets the whole of hacks.JSON and returns the dict
    server_url = config.get_setting("server_url") # Get server_url from config
    if not server_url:
        print("Error: Server URL not configured.")
        return None

    list_url = server_url.rstrip('/') + '/hacks.json' 

    try:
        response = requests.get(list_url, timeout=15) 
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hack list from {list_url}: {e}")
    except Exception as e: 
        print(f"An unexpected error occurred fetching hack list: {e}")
    return None


def download_patch_from_server(patch_url, config):
    # This downloads a patch from a url and returns its location
    # patch_url e.g. patches/Glazed8.6.3.ups

    patch_cache_dir = Path(config.get_setting("patch_dir", "downloaded_patches"))
    patch_cache_dir.mkdir(parents=True, exist_ok=True) # Ensure dir exists

    # This just gets the location of where the ROM hack is / should be
    local_patch_filename = Path(patch_url).name
    local_patch_path = patch_cache_dir / local_patch_filename

    # If we already have the patch then just return it
    if local_patch_path.exists():
        print(f"Patch already exists: {local_patch_path}")
        return str(local_patch_path) # Return string for consistency

    server_url = config.get_setting("server_url")
    if not server_url:
        print("Error: Server URL not configured. Cannot download patch.")
        return None

    download_url = server_url.rstrip('/') + '/' + patch_url.lstrip('/')
    print(f"Downloading patch: {download_url}")

    try:
        response = requests.get(download_url, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        with open(local_patch_path, 'wb') as f:
            f.write(response.content)
        print(f"Patch downloaded to: {local_patch_path}")
        return str(local_patch_path)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading patch from {download_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred downloading patch to {local_patch_path}: {e}")
    return None


def download_image_from_server(image_url, config):
    # This downloads the box art from the server, same as above
    # Uses a different way of downloading with copyfileobj - better for images

    # image_url e.g. images/Glazed8.6.3.png

    image_cache_dir = Path(config.get_setting("box_art_dir", "box_art"))
    image_cache_dir.mkdir(parents=True, exist_ok=True)

    local_image_filename = Path(image_url).name
    local_image_path = image_cache_dir / local_image_filename

    # If we already have the art then just return it
    if local_image_path.exists():
        return str(local_image_path)

    server_url = config.get_setting("server_url")
    if not server_url:
        print("Error: Server URL not configured. Cannot download image.")
        return None

    download_url = server_url.rstrip('/') + '/' + image_url.lstrip('/')
    print(f"Downloading image: {download_url}")

    try:
        response = requests.get(download_url, stream=True, timeout=15)
        response.raise_for_status()
        with open(local_image_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Image downloaded to: {local_image_path}")
        return str(local_image_path)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {download_url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred downloading image to {local_image_path}: {e}")
    return None