import customtkinter
from customtkinter import CTkFont, CTkImage
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
from PIL import Image

from populate_roms import RomListItemController, load_button_images
from app import RomLauncherService

# --- Configuration ---
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"
CUSTOM_FONT_NAME = "Cascadia Code SemiBold"

# --- Colors ---
HEADER_BG = "#8C1919"
CONTENT_BG = "#E7E7E7"
HEADER_FG = "#FFFFFF"

def relative_to_assets(path: str) -> Path:
    # A little helper to get the full path to an asset file.
    full_path = ASSETS_PATH / Path(path)
    if not full_path.is_file():
        print(f"Warning: Asset not found at {full_path}")
    return full_path

class MainApplication(customtkinter.CTk):
    # This is the main class for the whole GUI.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Core Application Logic ---
        self.service = RomLauncherService()

        # --- Window Setup ---
        self.title("PokeROM Launcher")
        self.geometry("1024x768")
        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")

        # --- Initialize UI Components ---
        self._setup_state_variables()
        self._create_fonts()
        self._setup_background()
        self._create_main_frames()
        self._create_header_widgets()
        self._create_main_content_widgets()
        self._setup_callbacks_and_caches()

        # --- Initial Data Load ---
        self.refresh_lists()

    def _setup_state_variables(self):
        # Set up the Tkinter variables and other internal state.
        self.current_view = tk.StringVar(value="installed")
        self.current_system_filter = tk.StringVar(value="All")
        self.current_base_rom_filter = tk.StringVar(value="All")

        # Keep references to any toplevel windows we create.
        self.install_window = None
        self.filter_window = None
        self.settings_window = None
        self.scrollable_frame = None

    def _setup_callbacks_and_caches(self):
        # Pre-load assets and set up callback dicts to be more efficient.
        self.rom_list_item_controllers = {}
        
        self.button_image_cache = {
            "installed": load_button_images(["Play", "Delete"], 2, ASSETS_PATH),
            "available": load_button_images(["Install"], 2, ASSETS_PATH)
        }
        
        self.list_item_callbacks = {
            "play": self.service.play_rom,
            "delete": self._handle_delete_action,
            "install": self.start_install_process
        }

    def _create_fonts(self):
        # Creates and stores all the fonts we'll need.
        self.fonts = {
            "title": CTkFont(family=CUSTOM_FONT_NAME, size=22),
            "body": CTkFont(family="Cascadia Code", size=15),
            "bold_body": CTkFont(family=CUSTOM_FONT_NAME, size=15, weight="bold"),
            "hyperlink": CTkFont(family=CUSTOM_FONT_NAME, size=15, underline=True),
            "header_title": CTkFont(family=CUSTOM_FONT_NAME, size=32, weight="bold")
        }

    def _setup_background(self):
        # Loads and configures the resizable background image.
        # Timer used to resize when window is resized
        self.background_label = customtkinter.CTkLabel(self, text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.lower()
        
        try:
            self.base_background_image = Image.open(relative_to_assets("background.png"))
        except Exception as e:
            print(f"Could not load background.png: {e}")
            self.base_background_image = None
        
        self.resize_timer = None
        self.bind("<Configure>", self._on_resize_debounced)

    def _perform_background_update(self):
        if not self.base_background_image: return
        win_width, win_height = self.winfo_width(), self.winfo_height()
        resized = self.base_background_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
        bg_image = CTkImage(resized, size=(win_width, win_height))
        self.background_label.configure(image=bg_image)
        self.background_label.image = bg_image

    def _on_resize_debounced(self, event):
        if self.resize_timer:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, self._perform_background_update)

    def _create_main_frames(self):
        # Creates the main layout frames for the header and content areas.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_frame = customtkinter.CTkFrame(self, height=85, fg_color=HEADER_BG, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)

        self.main_content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_rowconfigure(2, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

    def _create_header_widgets(self):
        # Populates the header with the title and nav buttons.
        header_label = customtkinter.CTkLabel(self.header_frame, text="PokeROM Launcher", text_color=HEADER_FG, font=self.fonts["header_title"])
        header_label.pack(side="left", padx=20, pady=10)

        header_button_frame = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        header_button_frame.pack(side="right", padx=10)

        my_hacks_button = customtkinter.CTkButton(header_button_frame, text="My Hacks", font=self.fonts["header_title"], fg_color="transparent", hover_color="#A32F2F", command=lambda: self._change_view("installed"))
        my_hacks_button.pack(side="left", padx=2)

        discover_button = customtkinter.CTkButton(header_button_frame, text="Discover", font=self.fonts["header_title"], fg_color="transparent", hover_color="#A32F2F", command=lambda: self._change_view("available"))
        discover_button.pack(side="left", padx=5)

        try:
            settings_icon = CTkImage(Image.open(relative_to_assets("button_3.png")))
            settings_button = customtkinter.CTkButton(header_button_frame, image=settings_icon, text="", width=32, fg_color="transparent", hover_color="#A32F2F", command=self.open_settings)
            settings_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Could not load settings icon: {e}")

    def _create_main_content_widgets(self):
        # Sets up the search bar, filter buttons, and title label.
        search_frame = customtkinter.CTkFrame(self.main_content_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Search...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", lambda event: self.refresh_lists())

        search_button = self._create_image_hover_button(search_frame, "Search", self.refresh_lists)
        search_button.grid(row=0, column=1, padx=(2, 2))

        filter_button = self._create_image_hover_button(search_frame, "Filter", self.open_filter_menu)
        filter_button.grid(row=0, column=2)

        self.title_label = customtkinter.CTkLabel(self.main_content_frame, text="", font=self.fonts["header_title"])
        self.title_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Create the scrollable frame once here and we're done with it.
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.main_content_frame, fg_color=CONTENT_BG, corner_radius=0)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # --- UI Action Handlers ---
    def _change_view(self, new_view):
        # Just sets the current view and kicks off a refresh.
        self.current_view.set(new_view)
        self.refresh_lists()
        
    def _handle_delete_action(self, rom_id, rom_name):
        # Handles the delete logic, including the confirmation box and list refresh.
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{rom_name}'?", icon="warning", parent=self):
            self.service.delete_rom(rom_id)
            self.refresh_lists() # Refresh the list after deleting something

    # --- Helper & Utility Methods ---

    def _create_image_hover_button(self, parent, base_name, command):
        # Makes a CTkButton with different images for normal and hover states.
        try:
            scale_factor = 1.8
            pil_normal = Image.open(relative_to_assets(f"{base_name} normal.png"))
            new_size = (int(pil_normal.width * scale_factor), int(pil_normal.height * scale_factor))
            img_normal = CTkImage(pil_normal.resize(new_size, Image.Resampling.NEAREST), size=new_size)
            pil_hover = Image.open(relative_to_assets(f"{base_name} hover.png"))
            img_hover = CTkImage(pil_hover.resize(new_size, Image.Resampling.NEAREST), size=new_size)
            
            button = customtkinter.CTkButton(parent, image=img_normal, text="", fg_color="transparent", hover=False, command=command)
            button.bind("<Enter>", lambda e: button.configure(image=img_hover))
            button.bind("<Leave>", lambda e: button.configure(image=img_normal))
            return button
        except Exception as e:
            print(f"Could not load button images for '{base_name}'. Error: {e}")
            return customtkinter.CTkButton(parent, text=base_name, width=80, command=command)

    def center_toplevel(self, toplevel: customtkinter.CTkToplevel, width: int, height: int):
        # Helper to centre a popup window on top of the main one.
        toplevel.update_idletasks()
        main_x, main_y = self.winfo_x(), self.winfo_y()
        main_width, main_height = self.winfo_width(), self.winfo_height()
        pos_x = main_x + (main_width // 2) - (width // 2)
        pos_y = main_y + (main_height // 2) - (height // 2)
        toplevel.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def browse_file(self, entry_widget):
        # Opens file explorer.
        filepath = filedialog.askopenfilename(parent=self.settings_window)
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def browse_directory(self, entry_widget):
        dirpath = filedialog.askdirectory(parent=self.settings_window)
        if dirpath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dirpath)
            


    # --- Core UI Functionality ---

    def refresh_lists(self):
        # This is how we refresh the list of ROMs without destroying everything.
        # It just hides all the widgets, then shows the ones we need for the current view.
        view = self.current_view.get()
        query = self.search_entry.get()
        system = self.current_system_filter.get()
        base_rom = self.current_base_rom_filter.get()
        
        system_parameter = system if system != "All" else None
        base_rom_parameter = base_rom if base_rom != "All" else None

        # 1. Figure out which data to show.
        if view == "installed":
            self.title_label.configure(text="My Installed Hacks")
            hacks = self.service.get_installed_hacks(query, system_parameter, base_rom_parameter)
        else: # "available"
            self.title_label.configure(text="Available Hacks")
            hacks = self.service.get_available_hacks(query, system_parameter, base_rom_parameter)

        self.title_label.update()

        # 2. Hide all the list items.
        for controller in self.rom_list_item_controllers.values():
            controller.hide()

        # 3. Now, create, update, and show only the widgets we need.
        if not hacks:
            # If we didn't find anything, we can just show an empty list.
            return

        for rom in hacks:
            if rom.id not in self.rom_list_item_controllers:
                # We only create a controller for a ROM the first time we see it.
                self.rom_list_item_controllers[rom.id] = RomListItemController(
                    parent=self.scrollable_frame,
                    rom=rom,
                    callbacks=self.list_item_callbacks,
                    fonts=self.fonts
                )
            
            # Grab the controller and tell it to show itself with the right buttons.
            controller = self.rom_list_item_controllers[rom.id]
            controller.update_view(view, self.button_image_cache[view])
            controller.show()

    def start_install_process(self, rom_id, rom_name):
        if self.install_window and self.install_window.winfo_exists():
            self.install_window.focus()
            return

        self.install_window = customtkinter.CTkToplevel(self)
        self.install_window.title("Installing")
        self.center_toplevel(self.install_window, 300, 100)
        self.install_window.transient(self)
        self.install_window.grab_set()
        self.install_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.install_window.resizable(False, False)

        label = customtkinter.CTkLabel(self.install_window, text=f"Installing {rom_name}...", font=self.fonts["body"])
        label.pack(expand=True, padx=20, pady=20)

        result_container = []
        def worker():
            result = self.service.install_hack(rom_id)
            result_container.append(result)

        def check_thread():
            if install_thread.is_alive():
                self.after(100, check_thread)
            else:
                self.install_window.destroy()
                if result_container:
                    result = result_container[0]
                    if result:
                        messagebox.showinfo("Success", "Installed successfully!", parent=self)
                    else:
                        messagebox.showerror("Error", "Could not install patch.", parent=self)
                else:
                    messagebox.showerror("Error", "An unknown error occurred.", parent=self)
                self.refresh_lists()
        
        install_thread = threading.Thread(target=worker)
        install_thread.start()
        check_thread()

    def open_filter_menu(self):
        # Allows users to filter by base ROM or system.
        if self.filter_window and self.filter_window.winfo_exists():
            self.filter_window.focus()
            return

        self.filter_window = customtkinter.CTkToplevel(self)
        self.filter_window.title("Filter Options")
        self.center_toplevel(self.filter_window, 350, 250)
        self.filter_window.transient(self)
        self.filter_window.grab_set()

        frame = customtkinter.CTkFrame(self.filter_window, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        frame.grid_columnconfigure(1, weight=1)

        # Temp variables for the dropdowns in this dialog.
        temp_system_var = tk.StringVar(value=self.current_system_filter.get())
        
        base_rom_ids = list(self.service.config.get_setting("base_roms", {}).keys())
        base_rom_display_options = ["All"] + [rom_id.title() for rom_id in base_rom_ids]
        
        # Figure out the display name that matches the current filter ID.
        current_base_rom_id = self.current_base_rom_filter.get()
        current_display = "All"
        if current_base_rom_id != "All":
            for name in base_rom_display_options:
                if name.lower() == current_base_rom_id:
                    current_display = name
                    break
        temp_base_rom_var = tk.StringVar(value=current_display)


        customtkinter.CTkLabel(frame, text="System:", font=self.fonts["bold_body"]).grid(row=0, column=0, sticky="w", pady=5)
        system_menu = customtkinter.CTkOptionMenu(frame, variable=temp_system_var, values=["All", "GBA", "NDS"], font=self.fonts["body"])
        system_menu.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        customtkinter.CTkLabel(frame, text="Base ROM:", font=self.fonts["bold_body"]).grid(row=1, column=0, sticky="w", pady=5)
        base_rom_menu = customtkinter.CTkOptionMenu(frame, variable=temp_base_rom_var, values=base_rom_display_options, font=self.fonts["body"])
        base_rom_menu.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        if not base_rom_ids: base_rom_menu.configure(state="disabled")

        def apply_filters():
            # Sets the main state variables and then refresh.
            selected_base_display = temp_base_rom_var.get()
            selected_base_id = selected_base_display.lower() if selected_base_display != "All" else "All"

            self.current_system_filter.set(temp_system_var.get())
            self.current_base_rom_filter.set(selected_base_id)
            
            self.filter_window.destroy()
            self.refresh_lists()

        def clear_filters():
            # Resets filters back to their defaults refresh.
            self.current_system_filter.set("All")
            self.current_base_rom_filter.set("All")

            self.filter_window.destroy()
            self.refresh_lists()

        button_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        customtkinter.CTkButton(button_frame, text="Apply", command=apply_filters).pack(side="left", padx=10)
        customtkinter.CTkButton(button_frame, text="Clear Filters", fg_color="#555", hover_color="#777", command=clear_filters).pack(side="left", padx=10)

    def open_settings(self):
        # Settings menu to configure paths to emulators and base ROMs.
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = customtkinter.CTkToplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("650x450")
        self.settings_window.transient(self)
        self.settings_window.grab_set()

        frame = customtkinter.CTkFrame(self.settings_window, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        def create_path_row(parent, label_text, initial_value, row, browse_func):
            customtkinter.CTkLabel(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
            entry = customtkinter.CTkEntry(parent)
            entry.insert(0, initial_value)
            entry.grid(row=row, column=1, sticky="ew", pady=4, padx=5)
            customtkinter.CTkButton(parent, text="Browse...", width=80, command=lambda: browse_func(entry)).grid(row=row, column=2, pady=4)
            return entry

        entries = {
            "emulator": create_path_row(frame, "Emulator Path:", self.service.config.get_setting("emulator_path", ""), 0, self.browse_file),
            "patched": create_path_row(frame, "Patched ROMs:", self.service.config.get_setting("patched_roms_dir", ""), 1, self.browse_directory),
            "box_art": create_path_row(frame, "Box Art Dir:", self.service.config.get_setting("box_art_dir", ""), 2, self.browse_directory)
        }
        
        base_rom_frame = customtkinter.CTkFrame(frame)
        base_rom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(20, 5))
        base_rom_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(base_rom_frame, text="Base ROM Paths", font=self.fonts["bold_body"]).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(5,10))
        
        base_rom_paths = self.service.config.get_setting("base_roms", {})
        base_rom_entries = {}
        for i, (rom_id, rom_path) in enumerate(base_rom_paths.items()):
            entry = create_path_row(base_rom_frame, f"{rom_id.title()}:", rom_path, i + 1, self.browse_file)
            base_rom_entries[rom_id] = entry

        def save_settings_action():
            new_base_roms = {rom_id: entry.get() for rom_id, entry in base_rom_entries.items()}
            settings_to_update = {
                "emulator_path": entries["emulator"].get(),
                "patched_roms_dir": entries["patched"].get(),
                "box_art_dir": entries["box_art"].get(),
                "base_roms": new_base_roms
            }
            result = self.service.update_settings(settings_to_update)
            messagebox.showinfo("Settings", result["message"], parent=self.settings_window)
            self.settings_window.destroy()
            self.refresh_lists()

        save_button = customtkinter.CTkButton(frame, text="Save Settings", command=save_settings_action)
        save_button.grid(row=4, column=0, columnspan=3, pady=20)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()