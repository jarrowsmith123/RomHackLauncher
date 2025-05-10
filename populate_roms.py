import os
from pathlib import Path
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from fetch import fetch_hack_list_from_server
from actions import play_rom_action, delete_rom_action, install_patch_action

# Global variable to store server data, which is literally just hacks.JSON
# I'm storing this on the server so that the ROM list can be updated without the user having to update their program
available_hacks_server_data = {}
fetched_data = fetch_hack_list_from_server()
available_hacks_server_data = {k: v for k, v in fetched_data.items()}

def create_list_item(parent_frame, item_data, window, app_config, list_refresh_callback):

    # This function creates the GUI item in the list that we can see on the right menu
    # Handles boxart and ROM information

    # list_refresh_callback is just the list refresh function we're passing in
    # This will be used by delete_rom_action

    title = item_data.get('title', 'Unknown Title')
    body = item_data.get('body', '')
    image_path_str = item_data.get('img')
    rom_path = item_data.get('path')

    item_frame = ttk.Frame(parent_frame, padding=10, style="Content.TFrame")
    item_frame.pack(pady=5, padx=5, fill="x")

    img_label_container = ttk.Frame(item_frame, style="Content.TFrame")
    img_label_container.grid(row=0, column=0, rowspan=3, padx=(0, 10), sticky='n')

    if image_path_str:
       try:
           image_path = Path(image_path_str)
           if image_path.is_file():
               pil_image = Image.open(image_path)
               tk_image = ImageTk.PhotoImage(pil_image)
               
               img_label = ttk.Label(img_label_container, image=tk_image, style="Content.TLabel")
               img_label.image = tk_image 
               img_label.pack(anchor='n')
           else: raise FileNotFoundError(f"Image file not found: {image_path}")
       except Exception as e:
           print(f"Failed to load image {image_path_str}: {e}")
           img_placeholder = tk.Frame(img_label_container, width=80, height=100, bg="#CCCCCC", relief='sunken', borderwidth=1)
           img_placeholder.pack(anchor='n')
           ttk.Label(img_placeholder, text="No Art", background="#CCCCCC").pack(expand=True)
    else:
        img_placeholder = tk.Frame(img_label_container, width=80, height=100, bg="#DDDDDD", relief='sunken', borderwidth=1)
        img_placeholder.pack(anchor='n')
        ttk.Label(img_placeholder, text="No Art", background="#DDDDDD").pack(expand=True)

    text_button_frame = ttk.Frame(item_frame, style="Content.TFrame")
    text_button_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
    item_frame.grid_columnconfigure(1, weight=1)

    title_label = ttk.Label(text_button_frame, text=title, style="ContentTitle.TLabel")
    title_label.pack(anchor="nw", fill="x")

    body_label = ttk.Label(text_button_frame, text=body, style="ContentBody.TLabel")
    body_label.pack(anchor="nw", fill="x", pady=(5,10))

    button_container_frame = ttk.Frame(text_button_frame, style="Content.TFrame")
    button_container_frame.pack(anchor="nw", pady=(5,0))
    # We have to pass in the actual GUI window into these functions as well as app_config to get our ROM paths
    # This doesn't feel very elegant but it works and it means I can finally sleep
    play_button = ttk.Button(
        button_container_frame, text="Play", style="ContentButton.TButton",
        command=lambda p=rom_path: play_rom_action(p, window, app_config)) # launches the rom
    play_button.pack(side="left", padx=(0,5))

    delete_button = ttk.Button(
        button_container_frame, text="Delete", style="ContentButton.TButton",
        command=lambda t=title, p=rom_path, w=item_frame: (
            delete_rom_action(t, p, w, window), # deletes the rom
            list_refresh_callback() # refresh lists, so if a ROM is deleted we can see
        ))
    delete_button.pack(side="left", padx=5)

def populate_installed_hacks_list(right_scrollable_frame, window, app_config, list_refresh_callback):
    # This is just the information in hacks.JSON
    global available_hacks_server_data

    # Clear existing widgets
    for widget in right_scrollable_frame.winfo_children():
        widget.destroy()

    roms_data = []
    # Gets directory for images and patched roms, makes the directory if not found
    patched_roms_dir = Path(app_config.get("patched_roms_dir", "patched_roms"))
    patched_roms_dir.mkdir(parents=True, exist_ok=True)
    box_art_dir = Path(app_config.get("box_art_dir", "box_art"))
    box_art_dir.mkdir(parents=True, exist_ok=True)

    try:
        for rom in os.listdir(patched_roms_dir):
            print(rom)
            if rom.endswith(".gba"):
                full_path_to_rom = patched_roms_dir / rom
                if full_path_to_rom.is_file():
                    # This stem is the hack id, e.g. Glazed8.6.3
                    rom_id = Path(rom).stem
                    print(rom_id)

                    # Default values, for e.g. if no internet 
                    # TODO this needs to be tested properly, I think its bad if no art is downloaded

                    display_title = rom_id.replace('_', ' ').replace('-', ' ').title()
                    display_description = "Description not available from server"
                    art_path = None

                    # Lookup the hack on the cached server data with the rom_id
                    hack_info = available_hacks_server_data.get(rom_id)

                    if hack_info:
                        display_title = hack_info.get("name", display_title)
                        display_description = hack_info.get("description", display_description)
                    else:
                        print(f"Info: No server entry for installed ROM ID: {rom_id}")

                    # We get the box art here. It is cached when the patch is installed to prevent loads of server requests

                    art_file = box_art_dir / f"{rom_id}.png"
                    if art_file.exists():
                        art_path = str(art_file)
                    # Store all important information for a ROM in a dict
                    # TODO will probably want to include the author here as well and give links / proper credit
                    rom_data = {
                        "title": display_title,
                        "path": str(full_path_to_rom),
                        "body": display_description,
                        "img": art_path, 
                    }
                    roms_data.append(rom_data)

    except OSError as e:
        ttk.Label(right_scrollable_frame, text=f"Error accessing directory:\n{e}", style="Content.TLabel", justify=tk.LEFT).pack(pady=10)
        return

    if not roms_data:
        ttk.Label(right_scrollable_frame, text="No patched ROMs (.gba) found.", style="Content.TLabel").pack(pady=10)
    else:
        for data_item in roms_data:
            create_list_item(right_scrollable_frame, data_item, window, app_config, list_refresh_callback)



def populate_available_hacks_list(left_scrollable_frame, window, app_config, list_refresh_callback):
    
    global available_hacks_server_data

    # Clear existing widgets
    for widget in left_scrollable_frame.winfo_children():
        widget.destroy()

    if not available_hacks_server_data: # Check if the dictionary is empty
        ttk.Label(left_scrollable_frame, text="No hacks available from the server.", style="Sidebar.TLabel").pack(pady=10)
        return

    installed_roms = []
    patched_roms_dir_str = app_config.get("patched_roms_dir")
    if patched_roms_dir_str:
        try:
            # Get list of installed roms
            installed_roms = [Path(f).stem for f in os.listdir(patched_roms_dir_str) if f.lower().endswith(".gba")]
        except OSError as e:
            print(f"Error reading patched ROMs directory: {e}")

    displayed_count = 0
    # Iterate through the dictionary, key is hack_id, value is hack_details
    for hack_id, hack_details in available_hacks_server_data.items():
        print("debug:", hack_id)
        if hack_id in installed_roms:
            continue # Skip if already installed

        item_frame = ttk.Frame(left_scrollable_frame, style="Sidebar.TFrame")
        item_frame.pack(fill="x", pady=2, padx=5)
        
        hack_name = hack_details.get('name')
        name_label = ttk.Label(item_frame, text=hack_name, style="ListButton.TButton", background="#F0F0F0")
        name_label.pack(side="left", fill="x", expand=True, padx=(0, 5))

        install_button = ttk.Button(item_frame, text="Install", style="ContentButton.TButton",
                                    command=lambda hd=hack_details: (
                                        install_patch_action(hd, window, app_config),
                                        list_refresh_callback()
                                    ))
        install_button.pack(side="right")
        displayed_count += 1

    # If no displayed_count then there are no hacks available to install
    if displayed_count == 0:

        ttk.Label(left_scrollable_frame, text="All available hacks installed.", style="Sidebar.TLabel", wraplength=300).pack(pady=10)
