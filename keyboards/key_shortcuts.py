import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from configuration_manager import ScreenInfo
from widgets.switch import AnimatedSwitch
import keyboard
import json
import os
import pywinstyles
from widgets.button import BouncingButton
from widgets.sliding_frames import SlidingFrame

# Dictionary to store shortcut remappings
shortcut_remappings = {}
SHORTCUT_FILE = "shortcuts.json"
SETTINGS_FILE = "settings/settings.json"

class KeyShortcutsView(SlidingFrame):
    def __init__(self, parent, controller):
        self.screen_info = ScreenInfo()
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller
        self.available_keys = self.get_available_keys()
        self.shortcut_mappings = []  # To display in the UI

        self.setup_ui()
        
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
        self.animated_switch = AnimatedSwitch(self, command=self.toggle_shortcuts)
        self.animated_switch.pack(pady=10)

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
        self.delete_from_button = BouncingButton(upper_button_frame, text="Delete \u2191", command=self.delete_last_from_dropdown)
        self.delete_from_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_to_button = BouncingButton(upper_button_frame, text="Delete \u2193", command=self.delete_last_to_dropdown)
        self.delete_to_button.pack(side=tk.LEFT, padx=5)
        
        self.add_button = BouncingButton(upper_button_frame, text="Add Shortcut", command=self.add_shortcut)
        self.add_button.pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=self.screen_info.window_width*0.8, height=self.screen_info.window_height*0.3)
        self.scrollable_frame.pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        # Add save and reset buttons
        self.save_button = BouncingButton(button_frame, text="Save Shortcuts", command=self.save_shortcuts)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = BouncingButton(button_frame, text="Reset", command=self.reset_shortcuts)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.back_button = BouncingButton(self, text="Back", command=self.controller.wrap_command(self.controller.go_back))
        self.back_button.pack(pady=10)

    def toggle_shortcuts(self):
        """Enable or disable all elements except the 'Back' button based on switch state."""
        state = "normal" if self.animated_switch.get() else "disabled"
        for widget in self.from_key_frame.winfo_children() + self.to_key_frame.winfo_children():
            widget.configure(state=state)
            
        for button in [self.add_button, self.delete_from_button, self.delete_to_button, self.save_button, self.reset_button]:
            button.configure(state=state)
            
        # temporarily unhook all hotkeys when disabled
        if state == "disabled":
            keyboard.unhook_all()
        else:
            self.apply_shortcuts()
            
        # Update the settings file with the new value of `enable_hotkey_remapping`
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings_data = json.load(f)
        else:
            settings_data = {}  # Create an empty dictionary if file doesn't exist

        settings_data["enable_hotkey_remapping"] = state == "normal"
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_data, f, indent=4)

    def dropdown_selected(self, idx, key_type):
        """Show the next dropdown when an item is selected."""
        if key_type == 'from' and idx < len(self.key_from_dropdowns) - 1:
            self.key_from_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)
        elif key_type == 'to' and idx < len(self.key_to_dropdowns) - 1:
            self.key_to_dropdowns[idx + 1].pack(side=tk.LEFT, padx=5, pady=5)

    def delete_last_from_dropdown(self):
        """Delete last visible 'from' dropdown."""
        visible_from_dropdowns = [dropdown for dropdown in self.key_from_dropdowns if dropdown.winfo_ismapped()]
        if len(visible_from_dropdowns) > 1:
            idx = self.key_from_dropdowns.index(visible_from_dropdowns[-2])
            self.key_from_vars[idx].set('')
            visible_from_dropdowns[-1].pack_forget()

    def delete_last_to_dropdown(self):
        """Delete last visible 'to' dropdown."""
        visible_to_dropdowns = [dropdown for dropdown in self.key_to_dropdowns if dropdown.winfo_ismapped()]
        if len(visible_to_dropdowns) > 1:
            idx = self.key_to_dropdowns.index(visible_to_dropdowns[-2])
            self.key_to_vars[idx].set('')
            visible_to_dropdowns[-1].pack_forget()

    def add_shortcut(self):
        """Add a new shortcut to the dictionary and update the UI."""
        keys_from = [var.get() for var in self.key_from_vars if var.get()]
        keys_to = [var.get() for var in self.key_to_vars if var.get()]

        if not keys_from or not keys_to:
            messagebox.showwarning("Input Error", "Please select keys for both from and to combinations.")
            return

        shortcut = {
            'modifiers': keys_from[:-1],  # Modifiers for 'from'
            'key': keys_from[-1],  # Last key in 'from' combination
            'to_modifiers': keys_to[:-1],  # Modifiers for 'to'
            'to_key': keys_to[-1]  # Last key in 'to' combination
        }
        from_combination = '+'.join(keys_from)
        shortcut_remappings[from_combination] = shortcut

        remapping = f"{' + '.join(keys_from)} -> {' + '.join(keys_to)}"
        self.shortcut_mappings.append(remapping)
        self.update_shortcut_list()

    def update_shortcut_list(self):
        """Update the list of shortcuts displayed in the scrollable frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for remapping in self.shortcut_mappings:
            ctk.CTkLabel(self.scrollable_frame, text=remapping).pack(pady=5)

    def save_shortcuts(self):
        """Save current shortcut remappings to a JSON file and register the hotkeys."""
        with open(SHORTCUT_FILE, "w") as f:
            json.dump(shortcut_remappings, f)

        self.apply_shortcuts()
        messagebox.showinfo("Success", "Shortcuts saved!")

    def apply_shortcuts(self):
        """Apply the shortcut remappings from the dictionary."""
        for key, shortcut in shortcut_remappings.items():
            self.register_hotkey(shortcut)

    def load_shortcuts(self):
        """Load shortcuts from a JSON file if it exists and apply them."""
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings_data = json.load(f)
                if "enable_hotkey_remapping" in settings_data:
                    self.animated_switch.set(settings_data["enable_hotkey_remapping"])
                    self.toggle_shortcuts()
        
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, "r") as f:
                saved_shortcuts = json.load(f)
                for key, mapping in saved_shortcuts.items():
                    shortcut_remappings[key] = mapping
                    from_keys = mapping['modifiers'] + [mapping['key']]
                    to_keys = mapping['to_modifiers'] + [mapping['to_key']]
                    remapping = f"{' + '.join(from_keys)} -> {' + '.join(to_keys)}"
                    self.shortcut_mappings.append(remapping)
                self.update_shortcut_list()
                
                # apply the shortcuts if the switch is enabled
                if self.animated_switch.get():
                    self.apply_shortcuts()
                else:
                    keyboard.unhook_all()

    def reset_shortcuts(self):
        """Reset all shortcuts by clearing the mappings."""
        self.shortcut_mappings = []
        shortcut_remappings.clear()
        self.update_shortcut_list()
        messagebox.showinfo("Reset", "All shortcuts have been reset.")
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, "w") as f:
                json.dump({}, f)
        keyboard.unhook_all()

    def register_hotkey(self, shortcut):
        """Register a hotkey using the keyboard library."""
        from_combination = '+'.join(shortcut['modifiers'] + [shortcut['key']])
        to_combination = '+'.join(shortcut['to_modifiers'] + [shortcut['to_key']])
        keyboard.remap_hotkey(from_combination, to_combination, suppress=True)
