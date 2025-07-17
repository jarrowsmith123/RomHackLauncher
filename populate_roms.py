from pathlib import Path
from tkinter import ttk, messagebox
import tkinter as tk
from PIL import Image, ImageTk

def create_base_list_item(parent_frame, rom):
    # Creates the widget and information to display each ROM in gui
    
    item_frame = ttk.Frame(parent_frame, padding=10, style="Content.TFrame")
    item_frame.pack(pady=5, padx=5, fill="x")

    # --- Image/Box Art ---
    img_label_container = ttk.Frame(item_frame, style="Content.TFrame")
    img_label_container.grid(row=0, column=0, rowspan=4, padx=(0, 15), sticky='n')

    try:
        box_art_dir = Path(rom.config.get_setting("box_art_dir"))
        image_path = box_art_dir / Path(rom.box_art_url).name
        if image_path.is_file():
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((160, 160), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            img_label = ttk.Label(img_label_container, image=tk_image, style="Content.TLabel")
            img_label.image = tk_image 
            img_label.pack(anchor='n')
        else:
            raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        print(f"Failed to load image for {rom.name}: {e}")
        img_placeholder = tk.Frame(img_label_container, width=160, height=160, bg="#CCCCCC")
        img_placeholder.pack(anchor='n')
        ttk.Label(img_placeholder, text="No Art", background="#CCCCCC").pack(expand=True)

    # --- Text and Buttons Container ---
    text_button_frame = ttk.Frame(item_frame, style="Content.TFrame")
    text_button_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
    text_button_frame.columnconfigure(0, weight=1)

    # --- Title ---
    name_label = ttk.Label(text_button_frame, text=rom.name, style="ContentTitle.TLabel")
    name_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

    # --- Description ---
    body_label = ttk.Label(text_button_frame, text=rom.description, style="ContentBody.TLabel")
    body_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
    
    body_label = ttk.Label(text_button_frame, text=rom.author, style="ContentBody.TLabel")
    body_label.grid(row=2, column=0, sticky="w", pady=(0, 11))

    # Create a single frame to hold Base ROM and Author info horizontally
    info_frame = ttk.Frame(text_button_frame, style="Content.TFrame")
    info_frame.grid(row=2, column=0, sticky="w", pady=(0, 10))

    # -- Base ROM Info --
    # Add the "Base:" label to the info_frame
    ttk.Label(info_frame, text="Base:", style="ContentBodyBold.TLabel").pack(side="left")

    # Determine the style for the base ROM name
    rom_name_style = "ContentBody.TLabel"
    if rom.base_rom_id == 'firered':
        rom_name_style = "FireRedText.TLabel"
    elif rom.base_rom_id == 'emerald':
        rom_name_style = "EmeraldText.TLabel"
        
    # Add the colored base ROM name label to the info_frame
    ttk.Label(info_frame, text=rom.base_rom_id, style=rom_name_style).pack(side="left")

    # -- Author Info --
    # Add some padding and the "Author:" label to the info_frame
    ttk.Label(info_frame, text="Author:", style="ContentBodyBold.TLabel").pack(side="left", padx=(20, 0))
    ttk.Label(info_frame, text=rom.author, style="ContentBody.TLabel").pack(side="left")

    # --- Button Frame ---
    button_frame = ttk.Frame(text_button_frame, style="Content.TFrame")
    button_frame.grid(row=3, column=0, sticky="w")

    return button_frame

def create_installed_list_item(parent_frame, rom, window, app, list_refresh_callback):
    # Creates a gui item for the Installed Hacks list
    button_frame = create_base_list_item(parent_frame, rom)

    play_button = ttk.Button(button_frame, text="Play", style="ContentButton.TButton",
                             command=lambda r_id=rom.id: app.play_rom(r_id))
    play_button.pack(side="left", padx=(0, 5))

    delete_button = ttk.Button(button_frame, text="Delete", style="ContentButton.TButton",
                               command=lambda t=rom.name, r_id=rom.id: (
                                   messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{t}'?", icon='warning', parent=window) and \
                                   app.delete_rom(r_id) and \
                                   list_refresh_callback()
                               ))
    delete_button.pack(side="left")

def create_available_list_item(parent_frame, rom, window, app, list_refresh_callback):
    # Creates a gui item for the Available Hacks list
    button_frame = create_base_list_item(parent_frame, rom)

    install_button = ttk.Button(button_frame, text="Install", style="ContentButton.TButton",
                                command=lambda r_id=rom.id: (
                                    app.install_hack(r_id), 
                                    list_refresh_callback()
                                ))
    install_button.pack(side="left")


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def populate_installed_hacks_list(scrollable_frame, window, app, list_refresh_callback, installed_hacks):
    clear_frame(scrollable_frame)
    if not installed_hacks:
        ttk.Label(scrollable_frame, text="No matching ROM hacks found.", style="ContentBody.TLabel").pack(pady=20)
    else:
        for rom in installed_hacks:
            create_installed_list_item(scrollable_frame, rom, window, app, list_refresh_callback)


def populate_available_hacks_list(scrollable_frame, window, app, list_refresh_callback, available_hacks):
    clear_frame(scrollable_frame)
    if not available_hacks:
        ttk.Label(scrollable_frame, text="No new ROM hacks available.", wraplength=300, style="ContentBody.TLabel").pack(pady=20, padx=10)
    else:
        for rom in available_hacks:
            create_available_list_item(scrollable_frame, rom, window, app, list_refresh_callback)