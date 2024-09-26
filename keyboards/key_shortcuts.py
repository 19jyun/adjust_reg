import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from configuration_manager import ScreenInfo
import keyboard
import json
import os

# Dictionary to store shortcut remappings
shortcut_remappings = {}
SHORTCUT_FILE = "shortcuts.json"

class KeyShortcutsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.available_keys = self.get_available_keys()
        self.shortcut_mappings = []  # To display in the UI
        self.screen_info = ScreenInfo()

        self.setup_ui()
        
        # Load and apply shortcuts when the program starts
        self.load_shortcuts()

    def get_available_keys(self):
        return {
            "A": "a", "B": "b", "C": "c", "D": "d",
            "E": "e", "F": "f", "G": "g", "H": "h",
            "I": "i", "J": "j", "K": "k", "L": "l",
            "M": "m", "N": "n", "O": "o", "P": "p",
            "Q": "q", "R": "r", "S": "s", "T": "t",
            "U": "u", "V": "v", "W": "w", "X": "x",
            "Y": "y", "Z": "z",
            # Numbers
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            # Special characters
            "`": "`", "-": "-", "=": "=", "[": "[", "]": "]",
            "\\": "\\", ";": ";", "'": "'", ",": ",", ".": ".", "/": "/",
            # Function keys
            "Esc": "esc", "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
            "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8", "F9": "f9",
            "F10": "f10", "F11": "f11", "F12": "f12",
            # Control keys
            "Tab": "tab", "Caps Lock": "caps lock", "Shift": "shift", "Ctrl": "ctrl",
            "Alt": "alt", "Space": "space", "Enter": "enter", "Backspace": "backspace",
            # Arrow keys
            "Up": "up", "Down": "down", "Left": "left", "Right": "right"
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

        upper_button_frame = ctk.CTkFrame(self)
        upper_button_frame.pack(pady=10)

        # Add and display shortcuts
        ctk.CTkButton(upper_button_frame, text="Delete \u2191", command=self.delete_last_from_dropdown).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(upper_button_frame, text="Delete \u2193", command=self.delete_last_to_dropdown).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(upper_button_frame, text="Add Shortcut", command=self.add_shortcut).pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=self.screen_info.window_width*0.8, height=self.screen_info.window_height*0.3)
        self.scrollable_frame.pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        # Add delete buttons for "from" and "to"
        ctk.CTkButton(button_frame, text="Save Shortcuts", command=self.save_shortcuts).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Reset", command=self.reset_shortcuts).pack(side=tk.LEFT, padx=10)

    def dropdown_selected(self, idx, key_type):
        # Show the next dropdown when an item is selected
        if key_type == 'from' and idx < len(self.key_from_dropdowns) - 1:
            self.key_from_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)  # Use pack to show next dropdown
        elif key_type == 'to' and idx < len(self.key_to_dropdowns) - 1:
            self.key_to_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)  # Use pack to show next dropdown

    # Function to delete last visible "from" dropdown
    def delete_last_from_dropdown(self):
        visible_from_dropdowns = [dropdown for dropdown in self.key_from_dropdowns if dropdown.winfo_ismapped()]
        if len(visible_from_dropdowns) > 1:
            idx = self.key_from_dropdowns.index(visible_from_dropdowns[-2])
            self.key_from_vars[idx].set('')  # Clear the previous dropdown value
            
            # Hide the last visible dropdown
            visible_from_dropdowns[-1].pack_forget()
            self.key_from_vars.pop()

    # Function to delete last visible "to" dropdown
    def delete_last_to_dropdown(self):
        visible_to_dropdowns = [dropdown for dropdown in self.key_to_dropdowns if dropdown.winfo_ismapped()]
        if len(visible_to_dropdowns) > 1:
            idx = self.key_to_dropdowns.index(visible_to_dropdowns[-2])
            self.key_to_vars[idx].set('')  # Clear the previous dropdown value
            
            # Hide the last visible dropdown
            visible_to_dropdowns[-1].pack_forget()
            self.key_to_vars.pop()

    def add_shortcut(self):
        keys_from = [var.get() for var in self.key_from_vars if var.get()]
        keys_to = [var.get() for var in self.key_to_vars if var.get()]

        if not keys_from or not keys_to:
            messagebox.showwarning("Input Error", "Please select keys for both from and to combinations.")
            return

        # Combine all the selected keys into a remapping
        shortcut = {
            'modifiers': keys_from[:-1],  # Modifiers for 'from'
            'key': keys_from[-1],  # Last key in 'from' combination
            'to_modifiers': keys_to[:-1],  # Modifiers for 'to'
            'to_key': keys_to[-1]  # Last key in 'to' combination
        }
        # Create a unique key by using the full 'from' key combination
        from_combination = '+'.join(keys_from)

        # Use the full combination as the key to avoid overwriting
        shortcut_remappings[from_combination] = shortcut

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
        """
        Save current shortcut remappings to a JSON file and register the hotkeys.
        """
        # Unregister all hotkeys before applying new ones

        with open(SHORTCUT_FILE, "w") as f:
            json.dump(shortcut_remappings, f)

        # Register all the shortcuts from the file
        self.apply_shortcuts()

        messagebox.showinfo("Success", "Shortcuts saved!")

    def apply_shortcuts(self):
        """
        Apply the shortcut remappings from the dictionary.
        """
        for key, shortcut in shortcut_remappings.items():
            self.register_hotkey(shortcut)

    def load_shortcuts(self):
        """
        Load shortcuts from a JSON file if it exists and apply them.
        """
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, "r") as f:
                saved_shortcuts = json.load(f)
                for key, mapping in saved_shortcuts.items():
                    # Restore the shortcut_remappings dictionary
                    shortcut_remappings[key] = mapping
                    # Update the UI display
                    from_keys = mapping['modifiers'] + [mapping['key']]
                    to_keys = mapping['to_modifiers'] + [mapping['to_key']]
                    remapping = f"{' + '.join(from_keys)} -> {' + '.join(to_keys)}"
                    self.shortcut_mappings.append(remapping)
                self.update_shortcut_list()

                # Register the shortcuts
                self.apply_shortcuts()

    def reset_shortcuts(self):
        """
        Reset all the shortcuts by clearing the mappings.
        """
        self.shortcut_mappings = []
        shortcut_remappings.clear()
        self.update_shortcut_list()
        messagebox.showinfo("Reset", "All shortcuts have been reset.")
        
        # Clear the file content and unregister all hotkeys
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, "w") as f:
                json.dump({}, f)
                
        keyboard.unhook_all()

    def register_hotkey(self, shortcut):
        """
        Register a hotkey using the keyboard library.
        Maps the 'from' key combination to the 'to' key combination.
        """
        from_combination = '+'.join(shortcut['modifiers'] + [shortcut['key']])
        to_combination = '+'.join(shortcut['to_modifiers'] + [shortcut['to_key']])

        keyboard.remap_hotkey(from_combination, to_combination, suppress=True)