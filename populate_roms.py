import customtkinter
from customtkinter import CTkImage
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from fetch import download_image_from_server

# --- Color Constants ---
EMERALD_GREEN = "#2E8B57"
FIRE_RED = "#C0392B"
SOUL_SILVER = "#8AC6D4"

HYPERLINK_BLUE = "#00529B"
BODY_TEXT_COLOR = "#555555"
BORDER_PURPLE = "#55526f" 

def load_button_images(image_names, scale_factor, assets_path):
    # A helper function to load and cache our button images.
    image_cache = {}
    for name in image_names:
        key_name = name.lower().replace(" ", "_")
        try:
            pil_normal = Image.open(assets_path / f"{name} normal.png")
            new_size = (int(pil_normal.width * scale_factor), int(pil_normal.height * scale_factor))
            resized_normal = pil_normal.resize(new_size, Image.Resampling.NEAREST)
            image_cache[f"{key_name}_normal"] = CTkImage(resized_normal, size=new_size)
            pil_hover = Image.open(assets_path / f"{name} hover.png")
            resized_hover = pil_hover.resize(new_size, Image.Resampling.NEAREST)
            image_cache[f"{key_name}_hover"] = CTkImage(resized_hover, size=new_size)
        except Exception as e:
            print(f"Warning: Failed to load image for button '{name}'. Error: {e}")
            return None
    return image_cache

class RomListItemController:
    # This class manages the widgets and state for a single ROM hack in the list.
    # We create one for each hack and then reuse it, showing or hiding as needed.

    def __init__(self, parent, rom, callbacks, fonts):
        self.parent = parent
        self.rom = rom
        self.callbacks = callbacks
        self.fonts = fonts
        self.widget = None
        self.button_frame = None
        self.last_view = None
        
        # Grabs the box art in the background so first load isn't really slow.
        if self.rom.box_art_url:
            ThreadPoolExecutor(max_workers=1).submit(
                download_image_from_server, self.rom.box_art_url, self.rom.config
            )

        self._create_base_widgets()

    def _create_base_widgets(self):
        # Creates the static parts of the item: frame, art, and text.
        self.widget = customtkinter.CTkFrame(self.parent, corner_radius=5, border_width=5, border_color=BORDER_PURPLE)
        self.widget.grid_columnconfigure(1, weight=1)

        try:
            box_art_dir = Path(self.rom.config.get_setting("box_art_dir"))
            image_path = box_art_dir / Path(self.rom.box_art_url).name
            if not image_path.is_file(): raise FileNotFoundError("Box art not on disk yet")
            box_art_image = CTkImage(Image.open(image_path), size=(160, 160))
            img_label = customtkinter.CTkLabel(self.widget, image=box_art_image, text="")
        except Exception as e:
            print(f"Could not load box art for {self.rom.name}: {e}")
            img_label = customtkinter.CTkLabel(self.widget, text="No Art", width=160, height=160, fg_color="#E0E0E0", font=self.fonts["body"])

        img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="n")

        text_button_frame = customtkinter.CTkFrame(self.widget, fg_color="transparent")
        text_button_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(0, 10), pady=10)

        customtkinter.CTkLabel(text_button_frame, text=self.rom.name, font=self.fonts["title"], anchor="w").pack(fill="x")
        customtkinter.CTkLabel(text_button_frame, text=self.rom.description, font=self.fonts["body"], text_color=BODY_TEXT_COLOR, wraplength=600, justify="left", anchor="w").pack(fill="x", pady=(0, 8))
        
        info_frame = customtkinter.CTkFrame(text_button_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 10))

        customtkinter.CTkLabel(info_frame, text="Base:", font=self.fonts["bold_body"]).pack(side="left")
        base_color = FIRE_RED if self.rom.base_rom_id == "firered" else EMERALD_GREEN if self.rom.base_rom_id == "emerald" else SOUL_SILVER
        customtkinter.CTkLabel(info_frame, text=self.rom.base_rom_id.title(), text_color=base_color, font=self.fonts["body"]).pack(side="left", padx=(4,0))

        customtkinter.CTkLabel(info_frame, text="Author:", font=self.fonts["bold_body"]).pack(side="left", padx=(20, 0))
        customtkinter.CTkLabel(info_frame, text=self.rom.author, font=self.fonts["body"]).pack(side="left", padx=(4,0))

        self.button_frame = customtkinter.CTkFrame(text_button_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", side="bottom")

    def update_view(self, view_type, image_cache):
        # Sets up the item's buttons for the current view ('installed' or 'available').
        if self.last_view == view_type:
            return
            
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if view_type == "installed":
            self._create_installed_buttons(image_cache)
        else: # "available"
            self._create_available_buttons(image_cache)
        
        self.last_view = view_type
        
    def _create_installed_buttons(self, image_cache):
        # Makes the Play and Delete buttons.
        if image_cache:
            play_button = customtkinter.CTkButton(self.button_frame, image=image_cache["play_normal"], text="", fg_color="transparent", hover=False, command=lambda: self.callbacks["play"](self.rom.id))
            play_button.bind("<Enter>", lambda event: play_button.configure(image=image_cache["play_hover"]))
            play_button.bind("<Leave>", lambda event: play_button.configure(image=image_cache["play_normal"]))
            play_button.pack(side="left", padx=(0, 5))

            delete_button = customtkinter.CTkButton(self.button_frame, image=image_cache["delete_normal"], text="", fg_color="transparent", hover=False, command=lambda: self.callbacks["delete"](self.rom.id, self.rom.name))
            delete_button.bind("<Enter>", lambda event: delete_button.configure(image=image_cache["delete_hover"]))
            delete_button.bind("<Leave>", lambda event: delete_button.configure(image=image_cache["delete_normal"]))
            delete_button.pack(side="left")
        else: # Fallback to text buttons if images failed to load.
            customtkinter.CTkButton(self.button_frame, text="Play", command=lambda: self.callbacks["play"](self.rom.id)).pack(side="left", padx=(0, 5))
            customtkinter.CTkButton(self.button_frame, text="Delete", command=lambda: self.callbacks["delete"](self.rom.id, self.rom.name)).pack(side="left")

    def _create_available_buttons(self, image_cache):
        # Makes the Install button.
        if image_cache:
            install_button = customtkinter.CTkButton(self.button_frame, image=image_cache["install_normal"], text="", fg_color="transparent", hover=False, command=lambda: self.callbacks["install"](self.rom.id, self.rom.name))
            install_button.bind("<Enter>", lambda event: install_button.configure(image=image_cache["install_hover"]))
            install_button.bind("<Leave>", lambda event: install_button.configure(image=image_cache["install_normal"]))
            install_button.pack(side="left", padx=(0, 0))
        else: # Fallback to a text button.
            customtkinter.CTkButton(self.button_frame, text="Install", command=lambda: self.callbacks["install"](self.rom.id, self.rom.name)).pack(side="left")

    def show(self):
        # Make the item's main frame visible.
        if self.widget:
            self.widget.pack(pady=5, padx=5, fill="x")

    def hide(self):
        # Hides the item's main frame without actually destroying it.
        if self.widget:
            self.widget.pack_forget()