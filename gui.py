import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from app import RomLauncherService
from populate_roms import populate_available_hacks_list, populate_installed_hacks_list

# This is the point of entry for now


app = RomLauncherService()


# Most of this GUI code is made with help from https://github.com/ParthJadhav/Tkinter-Designer.git

# --- Configuration ---
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"


# TODO add config for these
HEADER_BG = "#8C1919"
SIDEBAR_BG = "#FF1B1B"
CONTENT_BG = "#FFD0D0"
HEADER_FG = "#FFFFFF"
BODY_FG = "#555555"

# --- Main Window Setup ---
window = tk.Tk()
window.title("PokeROM Launcher")
window.geometry("1024x768")
window.configure(bg="#8C1919")

# --- Style Configuration ---
style = ttk.Style()
style.theme_use('clam')
# General Styles
style.configure("Header.TFrame", background=HEADER_BG)
style.configure("Header.TLabel", background=HEADER_BG, foreground=HEADER_FG, font=("Cascadia Code SemiBold", 25))
style.configure("Content.TFrame", background=CONTENT_BG)
style.configure("Content.TLabel", background=CONTENT_BG, font=("Cascadia Code", 10))
style.configure("ContentTitle.TLabel", background=CONTENT_BG, font=("Cascadia Code SemiBold", 16))
style.configure("ContentBody.TLabel", background=CONTENT_BG, foreground=BODY_FG, font=("Cascadia Code", 10), wraplength=600)
style.configure("ContentBodyBold.TLabel", background=CONTENT_BG, foreground=BODY_FG, font=("Cascadia Code SemiBold", 10), wraplength=600)
style.configure("ContentButton.TButton", font=("Cascadia Code SemiBold", 10))
# Header Navigation Button Styles
style.configure("Nav.TButton", background=HEADER_BG, foreground=HEADER_FG, font=("Cascadia Code SemiBold", 12), borderwidth=0)
style.map("Nav.TButton", background=[('active', '#A32F2F')]) # Slightly lighter on hover/press

style.configure("FireRedText.TLabel", foreground="#C0392B", background=CONTENT_BG, font=("Cascadia Code", 10))
style.configure("EmeraldText.TLabel", foreground="#2E8B57", background=CONTENT_BG, font=("Cascadia Code", 10))



# --- Main Layout Frames ---
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)

header_frame = ttk.Frame(window, style="Header.TFrame", height=70)
header_frame.grid(row=0, column=0, sticky="ew")
header_frame.grid_propagate(False)

# This is the main content area
main_content_frame = ttk.Frame(window, style="Content.TFrame")
main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
main_content_frame.grid_rowconfigure(2, weight=1) # The scrollable area is in in row 2
main_content_frame.grid_columnconfigure(0, weight=1)

# This variable will control which view is shown: "installed" or "available"
current_view = tk.StringVar(value="installed")

def refresh_lists(*args):
    # Refreshes displayed content either installed or available
    view = current_view.get()
    query = search_entry.get()
    
    clear_frame(scrollable_frame) # Clear previous content

    if view == "installed":
        title_label.config(text="My Installed Hacks")
        hacks = app.get_installed_hacks(search_query=query)
        populate_installed_hacks_list(scrollable_frame, window, app, refresh_lists, hacks)
    elif view == "available":
        title_label.config(text="Discover New Hacks")
        hacks = app.get_available_hacks(search_query=query)
        populate_available_hacks_list(scrollable_frame, window, app, refresh_lists, hacks)

# Listen for changes to the current_view variable and refresh the list
current_view.trace_add("write", refresh_lists)

# --- Header Content ---
header_label = ttk.Label(header_frame, text="PokeROM Launcher", style="Header.TLabel")
header_label.pack(side="left", padx=20, pady=10)

header_button_frame = ttk.Frame(header_frame, style="Header.TFrame")
header_button_frame.pack(side="right", padx=10)

# Navigation Buttons in the Header
my_hacks_button = ttk.Button(header_button_frame, text="My Hacks", style="Nav.TButton", command=lambda: current_view.set("installed"))
my_hacks_button.pack(side="left", padx=5)

discover_button = ttk.Button(header_button_frame, text="Discover", style="Nav.TButton", command=lambda: current_view.set("available"))
discover_button.pack(side="left", padx=5)

# Settings Button
settings_icon_path = "assets/button_3.png"
pil_img = Image.open(settings_icon_path)
settings_icon = ImageTk.PhotoImage(pil_img)
settings_button_main = ttk.Button(header_button_frame, image=settings_icon, command=lambda: open_settings(), style="Header.TButton")
settings_button_main.image = settings_icon
settings_button_main.pack(side="left", padx=5)


# --- Single Main Content Area ---
# TODO add filter
# Search and Filter bar
search_frame = ttk.Frame(main_content_frame, style="Content.TFrame")
search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
search_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(search_frame)
search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
search_entry.bind("<Return>", lambda event: refresh_lists())

search_button = ttk.Button(search_frame, text="Search", style="ContentButton.TButton", command=refresh_lists)
search_button.grid(row=0, column=1, padx=5)

filter_button = ttk.Button(search_frame, text="Filter", style="ContentButton.TButton", command=lambda: None) # Placeholder
filter_button.grid(row=0, column=2)

# Title Label for the current view
title_label = ttk.Label(main_content_frame, text="", font=("Inter SemiBold", 18), style="Content.TLabel")
title_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

def create_scrollable_area(parent):
    list_container = ttk.Frame(parent, style="Content.TFrame")
    list_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
    list_container.grid_rowconfigure(0, weight=1)
    list_container.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(list_container, bg=CONTENT_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
    scrollable_frame_content = ttk.Frame(canvas, style="Content.TFrame")

    scrollable_frame_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def _on_mousewheel(event):
        if scrollbar.get() != (0.0, 1.0):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    window.bind_all("<MouseWheel>", _on_mousewheel) # Bind to window to work everywhere

    canvas.create_window((0, 0), window=scrollable_frame_content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    return scrollable_frame_content

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# Create the single scrollable area
scrollable_frame = create_scrollable_area(main_content_frame)


# --- Settings Window Functionality ---
settings_window_ref = None

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

    # --- Widgets for settings (Emulator path, Dirs, Base ROMs) ---
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
    for rom_id, rom_path in app.config.get_setting("base_roms", {}).items(): 
        ttk.Label(base_rom_frame, text=f"{rom_id.replace('_', ' ').title()}:").grid(row=row_num, column=0, sticky="w", pady=2)
        entry = ttk.Entry(base_rom_frame, width=50)
        entry.insert(0, rom_path)
        entry.grid(row=row_num, column=1, sticky="ew", pady=2, padx=5)
        ttk.Button(base_rom_frame, text="Browse...", command=lambda e=entry, r_id=rom_id: browse_file(e, f"Select Base ROM for {r_id.replace('_', ' ').title()}", [("GBA ROMs", "*.gba"), ("All files", "*.*")])).grid(row=row_num, column=2, pady=2)
        base_rom_entries[rom_id] = entry
        row_num += 1

    def save_settings_action():
        settings_to_update = {
            "emulator_path": emu_path_entry.get(),
            "patched_roms_dir": patched_dir_entry.get(),
            "box_art_dir": box_art_dir_entry.get(),
            "base_roms": {rom_id: var.get() for rom_id, var in base_rom_entries.items()}
        }
        result = app.update_settings(settings_to_update)
        messagebox.showinfo("Settings", result['message'], parent=settings_window_ref)
        settings_window_ref.destroy()
        refresh_lists()

    save_button = ttk.Button(main_settings_frame, text="Save Settings", command=save_settings_action)
    save_button.grid(row=4, column=0, columnspan=3, pady=20)

def browse_file(entry_widget, title, filetypes):
    filepath = filedialog.askopenfilename(title=title, filetypes=filetypes, parent=settings_window_ref)
    if filepath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)

def browse_directory(entry_widget, title):
    dirpath = filedialog.askdirectory(title=title, parent=settings_window_ref)
    if dirpath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, dirpath)





# Initial population
refresh_lists()

# Start Main Loop
window.mainloop()