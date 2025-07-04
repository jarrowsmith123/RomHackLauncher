from pathlib import Path
from tkinter import ttk, messagebox
import tkinter as tk
from PIL import Image, ImageTk

# TODO this will be moved into gui.py

def create_installed_list_item(parent_frame, item_data, window, app, list_refresh_callback):
    """Creates a GUI item for the 'Installed Hacks' list on the right."""
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
               pil_image = pil_image.resize((160, 160), Image.Resampling.LANCZOS)
               tk_image = ImageTk.PhotoImage(pil_image)
               
               img_label = ttk.Label(img_label_container, image=tk_image, style="Content.TLabel")
               img_label.image = tk_image 
               img_label.pack(anchor='n')
           else: raise FileNotFoundError(f"Image file not found: {image_path}")
       except Exception as e:
           print(f"Failed to load image {image_path_str}: {e}")
           img_placeholder = tk.Frame(img_label_container, width=160, height=160, bg="#CCCCCC")
           img_placeholder.pack(anchor='n')
           ttk.Label(img_placeholder, text="No Art", background="#CCCCCC").pack(expand=True)
    else:
        img_placeholder = tk.Frame(img_label_container, width=160, height=160, bg="#DDDDDD")
        img_placeholder.pack(anchor='n')
        ttk.Label(img_placeholder, text="No Art", background="#DDDDDD").pack(expand=True)

    text_button_frame = ttk.Frame(item_frame, style="Content.TFrame")
    text_button_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
    text_button_frame.columnconfigure(0, weight=1)

    name_label = ttk.Label(text_button_frame, text=title, style="ContentTitle.TLabel")
    name_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

    body_label = ttk.Label(text_button_frame, text=body, style="ContentBody.TLabel")
    body_label.grid(row=1, column=0, sticky="w", pady=(0, 10))

    button_frame = ttk.Frame(text_button_frame, style="Content.TFrame")
    button_frame.grid(row=2, column=0, sticky="w")

    play_button = ttk.Button(button_frame, text="Play", style="ContentButton.TButton",
                             command=lambda p=rom_path: app.play_rom(p))
    play_button.pack(side="left", padx=(0, 5))

    delete_button = ttk.Button(button_frame, text="Delete", style="ContentButton.TButton",
                               command=lambda t=title, p=rom_path: (
                                   messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{t}'?\n({p})", icon='warning', parent=window) and \
                                   app.delete_rom(p) and \
                                   list_refresh_callback()
                               ))
    delete_button.pack(side="left")


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def populate_installed_hacks_list(right_scrollable_frame, window, app, list_refresh_callback):
    clear_frame(right_scrollable_frame)
    print("Populating installed ROMs list...")
    
    installed_hacks = app.get_installed_hacks()

    if not app.config.get_setting("patched_roms_dir"):
        ttk.Label(right_scrollable_frame, text="Patched ROMs directory not configured in settings.", style="ContentBody.TLabel").pack(pady=20)
        return

    if not installed_hacks:
        ttk.Label(right_scrollable_frame, text="No ROM hacks installed yet.", style="ContentBody.TLabel").pack(pady=20)
    else:
        for item_data in installed_hacks:
            create_installed_list_item(right_scrollable_frame, item_data, window, app, list_refresh_callback)


def populate_available_hacks_list(left_scrollable_frame, window, app, list_refresh_callback):
    clear_frame(left_scrollable_frame)
    print("Populating available ROMs list...")

    available_hacks = app.get_available_hacks()

    if not available_hacks:
        ttk.Label(left_scrollable_frame, text="No new ROM hacks available, or failed to fetch from server.", wraplength=300, style="ContentBody.TLabel").pack(pady=20, padx=10)
        return
    
    for hack_details in available_hacks:
        item_frame = ttk.Frame(left_scrollable_frame, style="Sidebar.TFrame")
        item_frame.pack(fill="x", pady=2, padx=5)
        
        hack_name = hack_details.get('name', 'Unknown Hack')
        hack_id = hack_details.get('id')

        name_label = ttk.Label(item_frame, text=hack_name, style="ListButton.TButton", background="#F0F0F0")
        name_label.pack(side="left", fill="x", expand=True, padx=(0, 5))

        install_button = ttk.Button(item_frame, text="Install", style="ContentButton.TButton",
                                    command=lambda i=hack_id: (app.install_hack(i), list_refresh_callback()))
        install_button.pack(side="right")