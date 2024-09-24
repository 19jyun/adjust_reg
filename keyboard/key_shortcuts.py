import ctypes
import customtkinter as ctk
import tkinter as tk
from ctypes import wintypes
from tkinter import messagebox
from configuration_manager import ScreenInfo
import threading
import win32con
import win32api
import win32gui

LRESULT = ctypes.c_long

# Dictionary to store shortcut remappings
shortcut_remappings = {}

# Define the callback type for the low-level keyboard hook
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Correct the function signature of the callback function
@LowLevelKeyboardProc
def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode == win32con.HC_ACTION:
        kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT))
        vkCode = kbd.contents.vkCode

        # Handle shortcut remapping
        handle_shortcut(vkCode)

    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

# Hook callback structure
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG),
    ]

# Function to handle the shortcut remapping
def handle_shortcut(vkCode):
    for shortcut, mapped in shortcut_remappings.items():
        if vkCode == shortcut['key']:
            # Simulate the remapped key combination
            for mod_key in mapped['modifiers']:
                win32api.keybd_event(mod_key, 0, 0, 0)
            win32api.keybd_event(mapped['key'], 0, 0, 0)
            win32api.keybd_event(mapped['key'], 0, win32con.KEYEVENTF_KEYUP, 0)
            for mod_key in mapped['modifiers']:
                win32api.keybd_event(mod_key, 0, win32con.KEYEVENTF_KEYUP, 0)
            break

# Function to set up the keyboard hook
def install_hook():
    WH_KEYBOARD_LL = 13
    # GetModuleHandle returns 64-bit, needs to be cast to a proper pointer type
    module_handle = ctypes.windll.kernel32.GetModuleHandleW(None)
    
    keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        low_level_keyboard_proc,
        module_handle,
        0
    )
    return keyboard_hook

# GUI class for the shortcut remapper
class KeyShortcutsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.available_keys = self.get_available_keys()

        self.shortcut_mappings = []  # To display in the UI

        self.screen_info = ScreenInfo()

        # Layout
        self.setup_ui()

    def get_available_keys(self):
        return {
            "A": 0x1E, "B": 0x30, "C": 0x2E, "D": 0x20,
            "E": 0x12, "F": 0x21, "G": 0x22, "H": 0x23,
            "I": 0x17, "J": 0x24, "K": 0x25, "L": 0x26,
            "M": 0x32, "N": 0x31, "O": 0x18, "P": 0x19,
            "Q": 0x10, "R": 0x13, "S": 0x1F, "T": 0x14,
            "U": 0x16, "V": 0x2F, "W": 0x11, "X": 0x2D,
            "Y": 0x15, "Z": 0x2C,
            # Numbers
            "0": 0x0B, "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05,
            "5": 0x06, "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A,
            # Special characters
            "`": 0x29, "-": 0x0C, "=": 0x0D, "[": 0x1A, "]": 0x1B,
            "\\": 0x2B, ";": 0x27, "'": 0x28, ",": 0x33, ".": 0x34, "/": 0x35,
            # Function keys
            "Esc": 0x01, "F1": 0x3B, "F2": 0x3C, "F3": 0x3D, "F4": 0x3E,
            "F5": 0x3F, "F6": 0x40, "F7": 0x41, "F8": 0x42, "F9": 0x43,
            "F10": 0x44, "F11": 0x57, "F12": 0x58,
            # Control keys
            "Tab": 0x0F, "Caps Lock": 0x3A, "Shift": 0x2A, "Left Ctrl": 0x1D,
            "Right Ctrl": 0x1D, "Left Alt": 0x38, "Right Alt": 0x38, "Space": 0x39,
            "Enter": 0x1C, "Backspace": 0x0E,
            # Arrow keys
            "Up": 0x48, "Down": 0x50, "Left": 0x4B, "Right": 0x4D,
            # Numpad keys
            "Numpad 0": 0x52, "Numpad 1": 0x4F, "Numpad 2": 0x50, "Numpad 3": 0x51,
            "Numpad 4": 0x4B, "Numpad 5": 0x4C, "Numpad 6": 0x4D, "Numpad 7": 0x47,
            "Numpad 8": 0x48, "Numpad 9": 0x49, "Numpad +": 0x4E, "Numpad -": 0x4A,
            "Numpad *": 0x37, "Numpad /": 0x35, "Numpad .": 0x53,
            # Other keys
            "Insert": 0x52, "Delete": 0x53, "Home": 0x47, "End": 0x4F,
            "Page Up": 0x49, "Page Down": 0x51, "Print Screen": 0x37, "Scroll Lock": 0x46,
            "Pause": 0x45, "Num Lock": 0x45,
            # Windows and Application keys
            "Left Win": 0x5B, "Right Win": 0x5C, "Application": 0x5D
        }

    def setup_ui(self):
        ctk.CTkLabel(self, text="Select Key Combination to Remap:").pack(pady=5)

        # Create frames to hold up to 4 keys for 'from' and 'to' combinations
        self.from_key_frame = ctk.CTkFrame(self)
        self.from_key_frame.pack(pady=5, fill="x")

        self.to_key_frame = ctk.CTkFrame(self)
        self.to_key_frame.pack(pady=5, fill="x")

        # Create arrays to hold the variables and dropdowns for 'from' and 'to' keys
        self.key_from_vars = [tk.StringVar() for _ in range(4)]
        self.key_to_vars = [tk.StringVar() for _ in range(4)]
        self.key_from_dropdowns = []
        self.key_to_dropdowns = []

        self.dropdown_width = self.screen_info.window_width // 4 - 10

        print(self.screen_info.window_width, self.dropdown_width)

        # Initialize the first dropdown visible and rest invisible
        for i in range(4):
            dropdown = ctk.CTkComboBox(self.from_key_frame, variable=self.key_from_vars[i], values=list(self.available_keys.keys()), 
                                    command=lambda value, idx=i: self.dropdown_selected(idx, 'from'), width=self.dropdown_width)
            dropdown.pack(side=tk.LEFT, padx=5, pady=5)
            self.key_from_dropdowns.append(dropdown)

            dropdown_to = ctk.CTkComboBox(self.to_key_frame, variable=self.key_to_vars[i], values=list(self.available_keys.keys()), 
                                        command=lambda value, idx=i: self.dropdown_selected(idx, 'to'), width=self.dropdown_width)
            dropdown_to.pack(side=tk.LEFT, padx=5, pady=5)
            self.key_to_dropdowns.append(dropdown_to)

            # Initially, only the first dropdown will be visible
            if i > 0:
                self.key_from_dropdowns[i].pack_forget()  # Hide the dropdown
                self.key_to_dropdowns[i].pack_forget()    # Hide the dropdown

        # Add and display shortcuts
        ctk.CTkButton(self, text="Add Shortcut", command=self.add_shortcut).pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scrollable_frame.pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Save Shortcuts", command=self.save_shortcuts).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Reset", command=self.reset_shortcuts).pack(side=tk.LEFT, padx=10)
        
    def dropdown_selected(self, idx, key_type):
        # Show the next dropdown when an item is selected
        if key_type == 'from' and idx < len(self.key_from_dropdowns) - 1:
            self.key_from_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)  # Use pack to show next dropdown
        elif key_type == 'to' and idx < len(self.key_to_dropdowns) - 1:
            self.key_to_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)  # Use pack to show next dropdown

        print(f"Selected from {key_type} dropdown {idx}")

    def add_shortcut(self):
        keys_from = [var.get() for var in self.key_from_vars if var.get()]
        keys_to = [var.get() for var in self.key_to_vars if var.get()]

        if not keys_from or not keys_to:
            messagebox.showwarning("Input Error", "Please select keys for both from and to combinations.")
            return

        # Combine all the selected keys into a remapping
        shortcut = {
            'modifiers': [self.available_keys[key] for key in keys_from if key],
            'key': self.available_keys[keys_from[-1]]  # Use the last as the main key
        }
        mapped = {
            'modifiers': [self.available_keys[key] for key in keys_to if key],
            'key': self.available_keys[keys_to[-1]]
        }
        shortcut_remappings[shortcut['key']] = mapped

        # Update UI
        remapping = f"{' + '.join(keys_from)} -> {' + '.join(keys_to)}"
        self.shortcut_mappings.append(remapping)
        self.update_shortcut_list()

    def update_shortcut_list(self):
        # Clear the current list in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Display each remapped key combination
        for remapping in self.shortcut_mappings:
            ctk.CTkLabel(self.scrollable_frame, text=remapping).pack(pady=5)

    def save_shortcuts(self):
        # Save shortcuts logic (optional)
        messagebox.showinfo("Success", "Shortcuts saved!")

    def reset_shortcuts(self):
        self.shortcut_mappings = []
        shortcut_remappings.clear()
        self.update_shortcut_list()
        messagebox.showinfo("Reset", "All shortcuts have been reset.")

# Running the hook in a separate thread
def run_hook():
    hook_id = install_hook()
    ctypes.windll.user32.GetMessageA(None, 0, 0, 0)

# Main function to start the program
if __name__ == "__main__":
    hook_thread = threading.Thread(target=run_hook)
    hook_thread.start()

    root = ctk.CTk()
    root.geometry("600x600")
    app = KeyShortcutsView(root, None)
    app.pack(fill="both", expand=True)
    root.mainloop()
