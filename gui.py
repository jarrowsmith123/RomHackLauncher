import customtkinter
from customtkinter import CTkFont, CTkImage
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

from pathlib import Path
from PIL import Image
import populate_roms 
from app import RomLauncherService

# --- Basic Setup ---
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

app = RomLauncherService()

# --- Configuration ---
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

# --- Colors ---
HEADER_BG = "#8C1919"
CONTENT_BG = "#E7E7E7"
HEADER_FG = "#FFFFFF"

def relative_to_assets(path: str) -> Path:
    full_path = ASSETS_PATH / Path(path)
    if not full_path.is_file():
        print(f"Warning: Asset not found at {full_path}")
    return full_path


CUSTOM_FONT_NAME = "Cascadia Code SemiBold" 

# --- Main Window Setup ---
window = customtkinter.CTk()
window.title("PokeROM Launcher")
window.geometry("1024x768")

# --- FONT DEFINITIONS  ---
fonts = {
    "title": CTkFont(family=CUSTOM_FONT_NAME, size=22),
    "body": CTkFont(family="Cascadia Code", size=15),
    "bold_body": CTkFont(family=CUSTOM_FONT_NAME, size=15, weight="bold"),
    "hyperlink": CTkFont(family=CUSTOM_FONT_NAME, size=15, underline=True),
    "header_title": CTkFont(family=CUSTOM_FONT_NAME, size=32, weight="bold")
}

# --- BACKGROUND IMAGE SETUP  ---
background_label = customtkinter.CTkLabel(window, text="")
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.lower() 

try:
    base_background_image = Image.open(relative_to_assets("background.png"))
except Exception as e:
    print(f"Could not load background.png, background will be a solid color. Error: {e}")
    base_background_image = None

# A variable to hold the timer ID
resize_timer = None

def perform_background_update():
    # Updates background image when timer finishes
    if not base_background_image:
        return

    win_width = window.winfo_width()
    win_height = window.winfo_height()

    # Resize the image to fit the window
    resized_image = base_background_image.resize((win_width, win_height), Image.Resampling.LANCZOS)

    # Create a CTkImage and update the background label
    bg_image = CTkImage(resized_image, size=(win_width, win_height))
    background_label.configure(image=bg_image)
    background_label.image = bg_image

def on_resize_debounced(event):
    # Call each window resize
    global resize_timer
    # Cancel the previous timer if it exists
    if resize_timer:
        window.after_cancel(resize_timer)
    
    # Set a new timer to call the update function after a delay
    resize_timer = window.after(250, perform_background_update)

# Bind the debounced function to the window's resize event
window.bind("<Configure>", on_resize_debounced)

# --- Main Layout Frames ---
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)
header_frame = customtkinter.CTkFrame(window, height=85, fg_color=HEADER_BG, corner_radius=0)
header_frame.grid(row=0, column=0, sticky="ew")
header_frame.grid_propagate(False)

main_content_frame = customtkinter.CTkFrame(window, fg_color="transparent")
main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
main_content_frame.grid_rowconfigure(2, weight=1)
main_content_frame.grid_columnconfigure(0, weight=1)
# --- State Management ---
current_view = tk.StringVar(value="installed")
install_modal_ref = None


def center_toplevel(toplevel: customtkinter.CTkToplevel, width: int, height: int):
    # Finds centre of window to put installing message
    toplevel.update_idletasks()
    
    # Get the main window's position and size
    main_x = window.winfo_x()
    main_y = window.winfo_y()
    main_width = window.winfo_width()
    main_height = window.winfo_height()

    # Calculate the position for the toplevel to be centered
    pos_x = main_x + (main_width // 2) - (width // 2)
    pos_y = main_y + (main_height // 2) - (height // 2)

    # Set the geometry with the calculated position
    toplevel.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def start_install_process(rom_id, rom_name):
    # Handles UI for patch installation
    global install_modal_ref
    
    if install_modal_ref and install_modal_ref.winfo_exists():
        install_modal_ref.focus()
        return

    # Create the modal "installing" window
    install_modal_ref = customtkinter.CTkToplevel(window)
    install_modal_ref.title("Installing")
    
    # Use the helper function to center the window reliably
    center_toplevel(install_modal_ref, width=300, height=100)
    
    install_modal_ref.transient(window)
    install_modal_ref.grab_set()
    install_modal_ref.protocol("WM_DELETE_WINDOW", lambda: None)
    install_modal_ref.resizable(False, False)

    label = customtkinter.CTkLabel(install_modal_ref, text=f"Installing {rom_name}...", font=fonts['body'])
    label.pack(expand=True, padx=20, pady=20)
    
    result_container = []
    # Multithreading to render both GUI elements
    def worker():
        result = app.install_hack(rom_id)
        result_container.append(result)

    def check_thread():
        if install_thread.is_alive():
            window.after(100, check_thread)
        else:
            install_modal_ref.destroy()
            if result_container:
                result = result_container[0]
                if result['success']:
                    messagebox.showinfo("Success", result['message'], parent=window)
                else:
                    messagebox.showerror("Error", result['message'], parent=window)
            else:
                messagebox.showerror("Error", "An unknown error occurred during installation.", parent=window)
            refresh_lists()
            
    install_thread = threading.Thread(target=worker)
    install_thread.start()
    check_thread()

def refresh_lists(*args):
    global scrollable_frame
    
    # Only recreate if view changed, not for searches
    view = current_view.get()
    query = search_entry.get()
    
    if not hasattr(refresh_lists, 'last_view'):
        refresh_lists.last_view = view
        refresh_lists.last_query = query
    
    view_changed = refresh_lists.last_view != view
    
    if view_changed and scrollable_frame:
        scrollable_frame.destroy()
        scrollable_frame = None
    
    if not scrollable_frame:
        scrollable_frame = customtkinter.CTkScrollableFrame(
            main_content_frame, 
            fg_color=CONTENT_BG, 
            corner_radius=0
        )
        scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Clear existing content instead of recreating frame
    if not view_changed:
        for child in scrollable_frame.winfo_children():
            child.destroy()
    
    # Update title
    if view == "installed":
        title_label.configure(text="My Installed Hacks")
        hacks = app.get_installed_hacks(search_query=query)
        populate_roms.populate_installed_hacks_list(
            scrollable_frame, window, app, refresh_lists, hacks, fonts
        )
    elif view == "available":
        title_label.configure(text="Discover New Hacks")
        hacks = app.get_available_hacks(search_query=query)
        populate_roms.populate_available_hacks_list(
            scrollable_frame, window, app, refresh_lists, hacks, fonts, start_install_process
        )
    
    refresh_lists.last_view = view
    refresh_lists.last_query = query

current_view.trace_add("write", refresh_lists)

# --- Header Content ---
header_label = customtkinter.CTkLabel(header_frame, text="PokeROM Launcher", text_color=HEADER_FG, font=fonts['header_title'])
header_label.pack(side="left", padx=20, pady=10)

header_button_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
header_button_frame.pack(side="right", padx=10)

my_hacks_button = customtkinter.CTkButton(header_button_frame, text="My Hacks", font=fonts['header_title'], fg_color="transparent", hover_color="#A32F2F", command=lambda: current_view.set("installed"))
my_hacks_button.pack(side="left", padx=2)

discover_button = customtkinter.CTkButton(header_button_frame, text="Discover",font=fonts['header_title'],  fg_color="transparent", hover_color="#A32F2F", command=lambda: current_view.set("available"))
discover_button.pack(side="left", padx=5)

try:
    settings_icon = CTkImage(Image.open(relative_to_assets("button_3.png")))
    settings_button_main = customtkinter.CTkButton(header_button_frame, image=settings_icon, text="", width=32, fg_color="transparent", hover_color="#A32F2F", command=lambda: open_settings())
    settings_button_main.pack(side="left", padx=5)
except Exception as e:
    print(f"Could not load settings icon: {e}")

# --- Single Main Content Area ---
search_frame = customtkinter.CTkFrame(main_content_frame, fg_color="transparent")
search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
search_frame.grid_columnconfigure(0, weight=1)

search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Search...")
search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
search_entry.bind("<Return>", lambda event: refresh_lists())


# Add search and Filter buttons
try:
    # Define the scale factor
    scale_factor = 1.8

    # Load and resize the normal image
    pil_search_normal = Image.open(relative_to_assets("Search normal.png"))
    new_size_search = (int(pil_search_normal.width * scale_factor), int(pil_search_normal.height * scale_factor))
    resized_search_normal = pil_search_normal.resize(new_size_search, Image.Resampling.NEAREST)
    search_normal_img = CTkImage(resized_search_normal, size=new_size_search)

    # Load and resize the hover image
    pil_search_hover = Image.open(relative_to_assets("Search hover.png"))
    resized_search_hover = pil_search_hover.resize(new_size_search, Image.Resampling.NEAREST)
    search_hover_img = CTkImage(resized_search_hover, size=new_size_search)
    
    search_button = customtkinter.CTkButton(
        search_frame, image=search_normal_img, text="", fg_color="transparent",
        hover=False, command=refresh_lists
    )
    search_button.bind("<Enter>", lambda e: search_button.configure(image=search_hover_img))
    search_button.bind("<Leave>", lambda e: search_button.configure(image=search_normal_img))

except Exception as e:
    print(f"Could not load Search button images. Error: {e}")
    search_button = customtkinter.CTkButton(search_frame, text="Search", width=80, command=refresh_lists)

search_button.grid(row=0, column=1, padx=(2, 2))

# Same as above
try:
    scale_factor = 1.8

    pil_filter_normal = Image.open(relative_to_assets("Filter normal.png"))
    new_size_filter = (int(pil_filter_normal.width * scale_factor), int(pil_filter_normal.height * scale_factor))
    resized_filter_normal = pil_filter_normal.resize(new_size_filter, Image.Resampling.NEAREST)
    filter_normal_img = CTkImage(resized_filter_normal, size=new_size_filter)

    pil_filter_hover = Image.open(relative_to_assets("Filter hover.png"))
    resized_filter_hover = pil_filter_hover.resize(new_size_filter, Image.Resampling.NEAREST)
    filter_hover_img = CTkImage(resized_filter_hover, size=new_size_filter)

    filter_button = customtkinter.CTkButton(
        search_frame, image=filter_normal_img, text="", fg_color="transparent",
        hover=False, command=lambda: None
    )
    filter_button.bind("<Enter>", lambda e: filter_button.configure(image=filter_hover_img))
    filter_button.bind("<Leave>", lambda e: filter_button.configure(image=filter_normal_img))

except Exception as e:
    print(f"Could not load Filter button images. Error: {e}")
    filter_button = customtkinter.CTkButton(search_frame, text="Filter", width=80, command=lambda: None)

filter_button.grid(row=0, column=2)

title_label = customtkinter.CTkLabel(main_content_frame, text="", font=fonts['header_title'])
title_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

scrollable_frame = None
settings_window_ref = None

def open_settings():
    # Handles settings menu
    global settings_window_ref
    if settings_window_ref and settings_window_ref.winfo_exists():
        settings_window_ref.focus()
        return

    settings_window_ref = customtkinter.CTkToplevel(window)
    settings_window_ref.title("Settings")
    settings_window_ref.geometry("650x450")
    settings_window_ref.transient(window)
    settings_window_ref.grab_set()

    main_settings_frame = customtkinter.CTkFrame(settings_window_ref, fg_color="transparent")
    main_settings_frame.pack(expand=True, fill="both", padx=10, pady=10)
    main_settings_frame.grid_columnconfigure(1, weight=1)

    def create_path_row(parent, label_text, initial_value, row, browse_func):
        customtkinter.CTkLabel(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        entry = customtkinter.CTkEntry(parent)
        entry.insert(0, initial_value)
        entry.grid(row=row, column=1, sticky="ew", pady=4, padx=5)
        button = customtkinter.CTkButton(parent, text="Browse...", width=80, command=lambda: browse_func(entry))
        button.grid(row=row, column=2, pady=4)
        return entry

    emu_path_entry = create_path_row(main_settings_frame, "Emulator Path:", app.config.get_setting("emulator_path", ""), 0, browse_file)
    patched_dir_entry = create_path_row(main_settings_frame, "Patched ROMs:", app.config.get_setting("patched_roms_dir", ""), 1, browse_directory)
    box_art_dir_entry = create_path_row(main_settings_frame, "Box Art Dir:", app.config.get_setting("box_art_dir", ""), 2, browse_directory)

    base_rom_frame = customtkinter.CTkFrame(main_settings_frame)
    base_rom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(20, 5))
    base_rom_frame.grid_columnconfigure(1, weight=1)
    customtkinter.CTkLabel(base_rom_frame, text="Base ROM Paths", font=fonts['bold_body']).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(5,10))
    
    # Iterates through base roms in config dict
    base_rom_entries = {}
    base_rom_paths = app.config.get_setting("base_roms", {})
    for i, (rom_id, rom_path) in enumerate(base_rom_paths.items()):
        row_num = i + 1
        entry = create_path_row(base_rom_frame, f"{rom_id.title()}:", rom_path, row_num, browse_file)
        base_rom_entries[rom_id] = entry

    def save_settings_action():
        new_base_roms = {rom_id: entry.get() for rom_id, entry in base_rom_entries.items()}
        settings_to_update = {
            "emulator_path": emu_path_entry.get(),
            "patched_roms_dir": patched_dir_entry.get(),
            "box_art_dir": box_art_dir_entry.get(),
            "base_roms": new_base_roms
        }
        result = app.update_settings(settings_to_update)
        messagebox.showinfo("Settings", result['message'], parent=settings_window_ref)
        settings_window_ref.destroy()
        refresh_lists()

    save_button = customtkinter.CTkButton(main_settings_frame, text="Save Settings", command=save_settings_action)
    save_button.grid(row=4, column=0, columnspan=3, pady=20)


# Opens file explorer
def browse_file(entry_widget):
    filepath = filedialog.askopenfilename(parent=settings_window_ref)
    if filepath: 
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)

def browse_directory(entry_widget):
    dirpath = filedialog.askdirectory(parent=settings_window_ref)
    if dirpath: 
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, dirpath)

# --- Initial Start ---
refresh_lists()
window.mainloop()