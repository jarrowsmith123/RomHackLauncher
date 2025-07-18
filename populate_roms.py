import customtkinter
from customtkinter import CTkImage
from tkinter import messagebox
from pathlib import Path
from PIL import Image
import webbrowser
from concurrent.futures import ThreadPoolExecutor

from fetch import download_image_from_server

# --- Color Constants ---
EMERALD_GREEN = "#2E8B57"
FIRE_RED = "#C0392B"
HYPERLINK_BLUE = "#00529B"
BODY_TEXT_COLOR = "#555555"
BORDER_PURPLE = "#55526f" 

def create_base_list_item_widgets(parent_frame, rom, fonts):

    item_frame = customtkinter.CTkFrame(parent_frame, corner_radius=5, border_width=5, border_color=BORDER_PURPLE)
    item_frame.pack(pady=5, padx=5, fill="x")
    item_frame.grid_columnconfigure(1, weight=1)

    try:
        box_art_dir = Path(rom.config.get_setting("box_art_dir"))
        image_path = box_art_dir / Path(rom.box_art_url).name
        if not image_path.is_file(): raise FileNotFoundError("Box art not found")
        box_art_image = CTkImage(Image.open(image_path), size=(160, 160))
        img_label = customtkinter.CTkLabel(item_frame, image=box_art_image, text="")

    except Exception as e:
        print(f"Could not load box art for {rom.name}: {e}")
        img_label = customtkinter.CTkLabel(item_frame, text="No Art", width=160, height=160, fg_color="#E0E0E0", font=fonts['body'])

    img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky='n')

    text_button_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
    text_button_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(0, 10), pady=10)

    customtkinter.CTkLabel(text_button_frame, text=rom.name, font=fonts['title'], anchor="w").pack(fill="x")
    customtkinter.CTkLabel(text_button_frame, text=rom.description, font=fonts['body'], text_color=BODY_TEXT_COLOR, wraplength=600, justify="left", anchor="w").pack(fill="x", pady=(0, 8))
    info_frame = customtkinter.CTkFrame(text_button_frame, fg_color="transparent")
    info_frame.pack(fill="x", pady=(0, 10))

    customtkinter.CTkLabel(info_frame, text="Base:", font=fonts['bold_body']).pack(side="left")
    base_color = FIRE_RED if rom.base_rom_id == 'firered' else EMERALD_GREEN if rom.base_rom_id == 'emerald' else BODY_TEXT_COLOR
    customtkinter.CTkLabel(info_frame, text=rom.base_rom_id.title(), text_color=base_color, font=fonts['body']).pack(side="left", padx=(4,0))

    customtkinter.CTkLabel(info_frame, text="Author:", font=fonts['bold_body']).pack(side="left", padx=(20, 0))
    customtkinter.CTkLabel(info_frame, text=rom.author, font=fonts['body']).pack(side="left", padx=(4,0))

    button_frame = customtkinter.CTkFrame(text_button_frame, fg_color="transparent")
    button_frame.pack(fill="x", side="bottom")
    return button_frame

def create_installed_list_item(parent_frame, rom, window, app, list_refresh_callback, fonts, image_cache):
    button_frame = create_base_list_item_widgets(parent_frame, rom, fonts)

    if image_cache:
        play_button = customtkinter.CTkButton(button_frame, image=image_cache['play_normal_img'], text="", fg_color="transparent", hover=False, command=lambda r_id=rom.id: app.play_rom(r_id))
        play_button.bind("<Enter>", lambda event: play_button.configure(image=image_cache['play_hover_img']))
        play_button.bind("<Leave>", lambda event: play_button.configure(image=image_cache['play_normal_img']))
        play_button.pack(side="left", padx=(0, 5))
        delete_button = customtkinter.CTkButton(button_frame, image=image_cache['delete_normal_img'], text="", fg_color="transparent", hover=False, command=lambda t=rom.name, r_id=rom.id: (messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{t}'?", icon='warning', parent=window) and app.delete_rom(r_id) and list_refresh_callback()))
        delete_button.bind("<Enter>", lambda event: delete_button.configure(image=image_cache['delete_hover_img']))
        delete_button.bind("<Leave>", lambda event: delete_button.configure(image=image_cache['delete_normal_img']))
        delete_button.pack(side="left")
    else:
        play_button = customtkinter.CTkButton(button_frame, text="Play", command=lambda r_id=rom.id: app.play_rom(r_id))
        play_button.pack(side="left", padx=(0, 5))
        delete_button = customtkinter.CTkButton(button_frame, text="Delete", command=lambda t=rom.name, r_id=rom.id: (messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{t}'?", icon='warning', parent=window) and app.delete_rom(r_id) and list_refresh_callback()))
        delete_button.pack(side="left")

def create_available_list_item(parent_frame, rom, window, app, list_refresh_callback, fonts, image_cache, install_handler):
    
    button_frame = create_base_list_item_widgets(parent_frame, rom, fonts)
    if image_cache:
        install_button = customtkinter.CTkButton(button_frame, image=image_cache['install_normal_img'], text="", fg_color="transparent", hover=False, command=lambda r_id=rom.id, r_name=rom.name: install_handler(r_id, r_name))
        install_button.bind("<Enter>", lambda event: install_button.configure(image=image_cache['install_hover_img']))
        install_button.bind("<Leave>", lambda event: install_button.configure(image=image_cache['install_normal_img']))
        install_button.pack(side="left", padx=(0, 0))
    else:
        install_button = customtkinter.CTkButton(button_frame, text="Install", command=lambda r_id=rom.id, r_name=rom.name: install_handler(r_id, r_name))
        install_button.pack(side="left")

def load_button_images(image_names, scale_factor, assets_path):
    image_cache = {}
    for name in image_names:
        key_name = name.lower().replace(" ", "_")
        try:
            pil_normal = Image.open(assets_path / f"{name} normal.png")
            new_size = (int(pil_normal.width * scale_factor), int(pil_normal.height * scale_factor))
            resized_normal = pil_normal.resize(new_size, Image.Resampling.NEAREST)
            image_cache[f'{key_name}_normal_img'] = CTkImage(resized_normal, size=new_size)
            pil_hover = Image.open(assets_path / f"{name} hover.png")
            resized_hover = pil_hover.resize(new_size, Image.Resampling.NEAREST)
            image_cache[f'{key_name}_hover_img'] = CTkImage(resized_hover, size=new_size)
        except Exception as e:
            print(f"Warning: Failed to load image for button '{name}'. Error: {e}")
            return None
    return image_cache

def populate_list(scrollable_frame, window, app, list_refresh_callback, hacks, fonts, create_item_func, button_image_info, **kwargs):
    if not hacks:
        no_items_text = "No new ROM hacks available." if "Install" in button_image_info[0] else "No installed hacks found."
        customtkinter.CTkLabel(scrollable_frame, text=no_items_text, font=fonts['body']).pack(pady=20)
        return
    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = [executor.submit(download_image_from_server, rom.box_art_url, rom.config) for rom in hacks if rom.box_art_url]
    assets_path = Path(__file__).parent / "assets"
    image_cache = load_button_images(*button_image_info, assets_path)
    for rom in hacks:
        create_item_func(scrollable_frame, rom, window, app, list_refresh_callback, fonts, image_cache, **kwargs)

def populate_installed_hacks_list(scrollable_frame, window, app, list_refresh_callback, hacks, fonts):
    populate_list(scrollable_frame, window, app, list_refresh_callback, hacks, fonts, create_installed_list_item, button_image_info=(["Play", "Delete"], 2))

def populate_available_hacks_list(scrollable_frame, window, app, list_refresh_callback, hacks, fonts, install_handler):
    populate_list(scrollable_frame, window, app, list_refresh_callback, hacks, fonts, create_available_list_item, button_image_info=(["Install"], 2), install_handler=install_handler)