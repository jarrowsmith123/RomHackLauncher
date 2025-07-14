import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from app import RomLauncherService
from populate_roms import populate_available_hacks_list, populate_installed_hacks_list

# This is the point of entry for now

app = RomLauncherService()

# --- Configuration ---
# Most of this GUI code is made with help from https://github.com/ParthJadhav/Tkinter-Designer.git

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

# TODO remove hard coded values
# Background colours, can implement a themes to change these
HEADER_BG = "#8C1919"
SIDEBAR_BG = "#F0F0F0"
CONTENT_BG = "#FFFFFF"
HEADER_FG = "#FFFFFF"
BODY_FG = "#555555"
 
# This just prevents code reuse getting full path of gui assets
def relative_to_assets(path: str) -> Path:
    full_path = ASSETS_PATH / Path(path)
    if not full_path.is_file():
        print(f"Warning: Asset not found at {full_path}")
    return full_path

# --- Main Window Setup ---
window = tk.Tk()
window.title("GBA ROM Launcher")
window.geometry("1200x700")
window.configure(bg="#E0E0E0")

# --- Style Configuration ---
style = ttk.Style()
style.theme_use('clam')
style.configure("Header.TFrame", background=HEADER_BG)
style.configure("Header.TLabel", background=HEADER_BG, foreground=HEADER_FG, font=("Inter SemiBold", 18))
style.configure("Sidebar.TFrame", background=SIDEBAR_BG)
style.configure("Content.TFrame", background=CONTENT_BG)
style.configure("Content.TLabel", background=CONTENT_BG, font=("Inter", 10))
style.configure("ContentTitle.TLabel", background=CONTENT_BG, font=("Inter SemiBold", 16))
style.configure("ContentBody.TLabel", background=CONTENT_BG, foreground=BODY_FG, font=("Inter", 10), wraplength=400)
style.configure("ContentButton.TButton", font=("Inter", 10))
style.configure("ListButton.TButton", anchor="w", font=("Inter", 12))

style.configure("Emerald.TLabel", background="#2E8B57", foreground="white", font=("Inter SemiBold", 12), padding=(5, 3))
style.configure("FireRed.TLabel", background="#C0392B", foreground="white", font=("Inter SemiBold", 12), padding=(5, 3))

# --- Main Layout Frames ---
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=4)

header_frame = ttk.Frame(window, style="Header.TFrame", height=70)
header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
header_frame.grid_propagate(False)

left_frame = ttk.Frame(window, width=350, style="Sidebar.TFrame")
left_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
left_frame.grid_propagate(False)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

right_frame = ttk.Frame(window, style="Content.TFrame")
right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
right_frame.grid_rowconfigure(2, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

header_button_frame = ttk.Frame(header_frame, style="Header.TFrame")
header_button_frame.pack(side="right", padx=10)


# Function that allows scrolling menus
# TODO this is broken lol
def create_scrollable_area(parent, container_style_name, canvas_bg_color, scrollable_frame_style_name=None):
    if scrollable_frame_style_name is None:
        scrollable_frame_style_name = container_style_name 

    list_container = ttk.Frame(parent, style=container_style_name)
    list_container.grid_rowconfigure(0, weight=1)
    list_container.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(list_container, bg=canvas_bg_color, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
    scrollable_frame_content = ttk.Frame(canvas, style=scrollable_frame_style_name)

    scrollable_frame_content.bind(
        "<Configure>",
        lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
    )
    canvas.bind_all("<Button-4>", lambda e, c=canvas: c.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e, c=canvas: c.yview_scroll(1, "units"))
    canvas.bind_all("<MouseWheel>", lambda e, c=canvas: c.yview_scroll(int(-1*(e.delta/120)), "units"))

    canvas.create_window((0, 0), window=scrollable_frame_content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    return list_container, scrollable_frame_content


# --- Left Sidebar Content ---
# This sidebar will contain the hacks that the user has not yet installed
# Search function does not work
# TODO Search fuction, nothing too complicated
# TODO add more information about the hack in this menu, or a pop up or something more informative

left_search_frame = ttk.Frame(left_frame, style="Sidebar.TFrame")
left_search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
left_search_frame.grid_columnconfigure(0, weight=1)
left_search_entry = ttk.Entry(left_search_frame)
left_search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
search_button_left = ttk.Button(left_search_frame, text="Search", command=lambda: None) # Search function here
search_button_left.grid(row=0, column=1, sticky="e")

left_list_label = ttk.Label(left_frame, text="Available Hacks", font=("Inter SemiBold", 14), background=SIDEBAR_BG)
left_list_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

left_list_container, left_scrollable_frame = create_scrollable_area(
    left_frame, "Sidebar.TFrame", SIDEBAR_BG
)
left_list_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

# --- Right Content Area ---
# This will contain the hacks that the user has installed
# TODO add search
# TODO add a filter to filter hacks by their base ROM
right_search_frame = ttk.Frame(right_frame, style="Content.TFrame")
right_search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
right_search_frame.grid_columnconfigure(0, weight=1)
right_search_entry = ttk.Entry(right_search_frame)
right_search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
filter_button = ttk.Button(right_search_frame, text="Search", style="ContentButton.TButton", command=lambda: None) # Placeholder action
filter_button.grid(row=0, column=1, padx=5)
action_button = ttk.Button(right_search_frame, text="Filter", style="ContentButton.TButton", command=lambda: None) # Placeholder action
action_button.grid(row=0, column=2)

right_list_label = ttk.Label(right_frame, text="Installed Hacks", font=("Inter SemiBold", 18), style="Content.TLabel")
right_list_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

right_list_container, right_scrollable_frame = create_scrollable_area(
    right_frame, "Content.TFrame", CONTENT_BG
)
right_list_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
right_scrollable_frame.grid_columnconfigure(0, weight=0)
right_scrollable_frame.grid_columnconfigure(1, weight=1)


# --- Settings Window Functionality ---
# Settings allows the user to set paths to emulator, ROM directory and such
# Saves information to config.JSON
settings_window_ref = None

def browse_file(entry_widget, title="Select File", filetypes=[("All files", "*.*")]):
    current_path = entry_widget.get()
    initial_dir = Path(current_path).parent if current_path and Path(current_path).exists() else "/"
    filepath = filedialog.askopenfilename(title=title, initialdir=str(initial_dir), filetypes=filetypes, parent=settings_window_ref)
    if filepath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)

def browse_directory(entry_widget, title="Select Directory"):
    current_path = entry_widget.get()
    initial_dir = current_path if current_path and Path(current_path).is_dir() else "/"
    dirpath = filedialog.askdirectory(title=title, initialdir=str(initial_dir), parent=settings_window_ref)
    if dirpath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, dirpath)

def open_settings():
    global settings_window_ref
    if settings_window_ref and settings_window_ref.winfo_exists():
        settings_window_ref.focus()
        return

    settings_window_ref = tk.Toplevel(window)
    settings_window_ref.title("Settings")
    settings_window_ref.geometry("650x550")
    settings_window_ref.transient(window)
    settings_window_ref.grab_set()

    main_settings_frame = ttk.Frame(settings_window_ref, padding=10)
    main_settings_frame.pack(expand=True, fill="both")
    main_settings_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(main_settings_frame, text="Emulator Path:").grid(row=0, column=0, sticky="w", pady=2)
    emu_path_entry = ttk.Entry(main_settings_frame, width=60)
    emu_path_entry.insert(0, app.config.get_setting("emulator_path", ""))
    emu_path_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
    ttk.Button(main_settings_frame, text="Browse...", command=lambda: browse_file(emu_path_entry, "Select Emulator", [("Executable files", "*.exe"), ("All files", "*.*")])).grid(row=0, column=2, pady=2)

    ttk.Label(main_settings_frame, text="Patched ROMs Directory:").grid(row=1, column=0, sticky="w", pady=2)
    patched_dir_entry = ttk.Entry(main_settings_frame, width=60)
    patched_dir_entry.insert(0, app.config.get_setting("patched_roms_dir", ""))
    patched_dir_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
    ttk.Button(main_settings_frame, text="Browse...", command=lambda: browse_directory(patched_dir_entry, "Select Patched ROMs Directory")).grid(row=1, column=2, pady=2)
    
    ttk.Label(main_settings_frame, text="Box Art Directory:").grid(row=2, column=0, sticky="w", pady=2)
    box_art_dir_entry = ttk.Entry(main_settings_frame, width=60)
    box_art_dir_entry.insert(0, app.config.get_setting("box_art_dir", "box_art"))
    box_art_dir_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
    ttk.Button(main_settings_frame, text="Browse...", command=lambda: browse_directory(box_art_dir_entry, "Select Box Art Directory")).grid(row=2, column=2, pady=2)

    base_rom_frame = ttk.LabelFrame(main_settings_frame, text="Base ROM Paths", padding=10)
    base_rom_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 5))
    base_rom_frame.grid_columnconfigure(1, weight=1)
    base_rom_entries = {}

    row_num = 0
    # Populate the settings menu with each base ROM in config and allows user to select ROM path
    for rom_id, rom_path in app.config.get_setting("base_roms", {}).items(): 
        ttk.Label(base_rom_frame, text=f"{rom_id.replace('_', ' ').title()}:").grid(row=row_num, column=0, sticky="w", pady=2)
        entry = ttk.Entry(base_rom_frame, width=50)
        entry.insert(0, rom_path)
        entry.grid(row=row_num, column=1, sticky="ew", pady=2, padx=5)
        ttk.Button(base_rom_frame, text="Browse...", command=lambda e=entry, r_id=rom_id: browse_file(e, f"Select Base ROM for {r_id.replace('_', ' ').title()}", [("GBA ROMs", "*.gba"), ("All files", "*.*")])).grid(row=row_num, column=2, pady=2)
        base_rom_entries[rom_id] = entry
        row_num += 1


    # Saves all the paths to the config,JSON
    def save_settings_action():

        # Get values from Tkinter entry widgets
        settings_to_update = {
            "emulator_path": emu_path_entry.get(),
            "patched_roms_dir": patched_dir_entry.get(),
            "box_art_dir": box_art_dir_entry.get(),
            "base_roms": {rom_id: var.get() for rom_id, var in base_rom_entries.items()}
        }
        result = app.update_settings(settings_to_update)
        
        messagebox.showinfo("Settings", result['message'], parent=settings_window_ref)
        settings_window_ref.destroy()
        
        # Repopulate lists as paths might have changed
        refresh_lists()

    save_button = ttk.Button(main_settings_frame, text="Save Settings", command=save_settings_action)
    save_button.grid(row=4, column=0, columnspan=3, pady=20)


# --- Header Content ---
# Header has title and settings button

header_label = ttk.Label(header_frame, text="GBA ROM Launcher", style="Header.TLabel")
header_label.pack(side="left", padx=20, pady=10)

settings_icon_path = relative_to_assets("button_3.png")
pil_img = Image.open(settings_icon_path)
settings_icon = ImageTk.PhotoImage(pil_img)
settings_button_main = ttk.Button(header_button_frame, image=settings_icon, command=open_settings, style="Header.TButton")
settings_button_main.image = settings_icon
settings_button_main.pack(side="right", padx=5)


def refresh_lists():
    # This is a hacky little way to pass the refresh into the populate roms to stop circular dependency
    # Im not used to this issue so I'm not sure if it is the best way to handle it
    print("Refreshing lists")

    populate_installed_hacks_list(right_scrollable_frame, window, app, refresh_lists)
    populate_available_hacks_list(left_scrollable_frame, window, app, refresh_lists)


# Initial population
refresh_lists()

# Start Main Loop
window.mainloop()