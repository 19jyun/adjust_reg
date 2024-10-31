import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from configuration_manager import ScreenInfo
from widgets.switch import AnimatedSwitch
import keyboard
import json
import os
from widgets.sliding_frames import SlidingFrame
from widgets.theme_manager import register_theme_change_callback

# Dictionary to store shortcut remappings
shortcut_remappings = {}
SHORTCUT_FILE = "shortcuts.json"
SETTINGS_FILE = "settings/settings.json"

class BouncingButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        self.single_click_command = kwargs.pop('command', None)
        super().__init__(*args, **kwargs)
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.single_click_command:
            self.single_click_command()  # 단일 클릭 시 한 번만 실행되도록 수정

class KeyShortcutsView(SlidingFrame):
    def __init__(self, parent, controller):
        self.screen_info = ScreenInfo()
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller
        self.available_keys = self.get_available_keys()
        self.shortcut_mappings = []  # To display in the UI

        scroll_width = self.screen_info.window_width
        scroll_height = self.screen_info.window_height
        self.container_frame = ctk.CTkScrollableFrame(self, width=scroll_width, height=scroll_height)
        self.container_frame.pack(fill="both", expand=True)

        # Define dropdown and button dimensions
        self.dropdown_width = (scroll_width - 20) // 4
        self.button_width = (scroll_width - 20) // 3
        
        # number of selected dropdowns
        # if 0, only one blank dropdown is displayed
        # if 1, two dropdowns (1 blank, 1 selected) are displayed
        # if 2, three dropdowns (1 blank, 2 selected) are displayed
        # if 3, four dropdowns (1 blank, 3 selected) are displayed
        # if 4, four dropdowns (all selected) are displayed

        self.dropdown_idx = [0, 0]
        


        self.setup_ui()
        self.update_idletasks()
        self.load_settings_and_shortcuts()

    def get_available_keys(self):
        # Define key mappings
        return {
            "A": "a", "B": "b", "C": "c", "D": "d",
            "E": "e", "F": "f", "G": "g", "H": "h",
            "I": "i", "J": "j", "K": "k", "L": "l",
            "M": "m", "N": "n", "O": "o", "P": "p",
            "Q": "q", "R": "r", "S": "s", "T": "t",
            "U": "u", "V": "v", "W": "w", "X": "x",
            "Y": "y", "Z": "z",
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            "`": "`", "-": "-", "=": "=", "[": "[", "]": "]",
            "\\": "\\", ";": ";", "'": "'", ",": ",", ".": ".", "/": "/",
            "Esc": "esc", "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
            "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8", "F9": "f9",
            "F10": "f10", "F11": "f11", "F12": "f12",
            "Tab": "tab", "Caps Lock": "caps lock", "Shift": "shift", "Ctrl": "ctrl",
            "Alt": "alt", "Space": "space", "Enter": "enter", "Backspace": "backspace",
            "Up": "up", "Down": "down", "Left": "left", "Right": "right"
        }

    def setup_ui(self):
        # Initialize the switch and bind the toggle method
        self.animated_switch = AnimatedSwitch(self.container_frame, command=self.toggle_shortcuts)
        register_theme_change_callback(self.animated_switch.update_theme)
        self.animated_switch.pack(pady=10)

        # UI components
        ctk.CTkLabel(self.container_frame, text="Select Key Combination to Remap:").pack(pady=5)
        self.from_key_frame = ctk.CTkFrame(self.container_frame)
        self.from_key_frame.pack(pady=5, fill="x")
        self.to_key_frame = ctk.CTkFrame(self.container_frame)
        self.to_key_frame.pack(pady=5, fill="x")

        # Define key dropdowns
        self.key_from_vars = [ctk.StringVar() for _ in range(4)]
        self.key_to_vars = [ctk.StringVar() for _ in range(4)]
        
        self.dropdown_lists = [[],[]]
        
        self.key_from_dropdowns = []
        self.key_to_dropdowns = []

        for i in range(0, 4):
            dropdown_from = ctk.CTkComboBox(self.from_key_frame, variable=self.key_from_vars[i], values=list(self.available_keys.keys()), 
                                            command=lambda value, idx=i : self.change_dropdown(0, 'dropdown', idx), width=self.dropdown_width)
            dropdown_from.pack(side=tk.LEFT, padx=5, pady=5)
            self.dropdown_lists[0].append(dropdown_from)

            dropdown_to = ctk.CTkComboBox(self.to_key_frame, variable=self.key_to_vars[i], values=list(self.available_keys.keys()), 
                                          command=lambda value, idx=i : self.change_dropdown(1, 'dropdown', idx), width=self.dropdown_width)
            dropdown_to.pack(side=tk.LEFT, padx=5, pady=5)
            self.dropdown_lists[1].append(dropdown_to)

            if i > 0:
                dropdown_from.pack_forget()
                dropdown_to.pack_forget()

        # Add control buttons
        upper_button_frame = ctk.CTkFrame(self.container_frame)
        upper_button_frame.pack(pady=10)

        self.delete_from_button = BouncingButton(upper_button_frame, text="Delete \u2191", command=lambda: self.change_dropdown(0, 'button'), width=self.button_width)
        self.delete_from_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_to_button = BouncingButton(upper_button_frame, text="Delete \u2193", command=lambda: self.change_dropdown(1, 'button'), width=self.button_width)
        self.delete_to_button.pack(side=tk.LEFT, padx=5)
        
        self.add_button = BouncingButton(upper_button_frame, text="Add Shortcut", command=self.add_shortcut, width=self.button_width)
        self.add_button.pack(pady=10)

        # Scrollable frame for displaying shortcut mappings
        self.scrollable_frame = ctk.CTkScrollableFrame(self.container_frame, width=self.screen_info.window_width*0.8, height=self.screen_info.window_height*0.3)
        self.scrollable_frame.pack(pady=10)

        # Save and reset buttons
        button_frame = ctk.CTkFrame(self.container_frame)
        button_frame.pack(pady=10)

        self.save_button = BouncingButton(button_frame, text="Save Shortcuts", command=self.save_shortcuts)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        self.reset_button = BouncingButton(button_frame, text="Reset", command=self.reset_shortcuts)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.back_button = BouncingButton(self.container_frame, text="Back", command=self.controller.wrap_command(self.controller.go_back))
        self.back_button.pack(pady=10)

    def load_settings_and_shortcuts(self):
        """Load settings from settings.json and apply initial shortcut remapping settings."""
        # Load settings
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings_data = json.load(f)
                remapping_enabled = settings_data.get("enable_hotkey_remapping", False)
                self.animated_switch.set(remapping_enabled)  # Set switch based on settings
                self.toggle_shortcuts()  # Update UI elements based on switch state

        # Load shortcuts
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

                if self.animated_switch.get():
                    self.apply_shortcuts()

    def toggle_shortcuts(self):
        """Enable or disable UI elements based on switch state."""
        state = "normal" if self.animated_switch.get() else "disabled"
        self.toggle_widgets(state)

        # Unhook or apply hotkeys based on switch state
        if state == "disabled":
            keyboard.unhook_all()
        else:
            self.apply_shortcuts()

        # Update settings file with new switch state
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings_data = json.load(f)
        else:
            settings_data = {}

        settings_data["enable_hotkey_remapping"] = state == "normal"
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_data, f, indent=4)

    def toggle_widgets(self, state):
        """Enable or disable interactive widgets in the given frame, excluding the back button."""
        for widget in self.from_key_frame.winfo_children() + self.to_key_frame.winfo_children():
            widget.configure(state=state)

        for button in [self.add_button, self.delete_from_button, self.delete_to_button, self.save_button, self.reset_button]:
            button.configure(state=state)

    def change_dropdown(self, key_type, caller, idx_dropdown=None):
        
        if idx_dropdown is not None:
            if idx_dropdown < self.dropdown_idx[key_type]:
                return
            
        increment = 0
        
        if caller == 'dropdown':
            increment = 1
        elif caller == 'button':
            increment = -1
    
        print("Called from: ", caller)
        
        if self.dropdown_idx[key_type] == 4 and caller == 'dropdown': # already full
            pass
        elif self.dropdown_idx[key_type] == 0 and caller == 'button': # already empty
            pass
        else:
            self.dropdown_idx[key_type] += increment
        
        self.update_dropdowns(key_type)
            
    def update_dropdowns(self, key_type):
        
        if self.dropdown_idx[key_type] == 4:
            pass
        
        else:
            for i in range(0, self.dropdown_idx[key_type]+1):
                self.dropdown_lists[key_type][i].pack(side=tk.LEFT, padx=5, pady=5)
                
            if self.dropdown_idx[key_type] == 3:
                self.dropdown_lists[key_type][3].set('')
                
            try:  # try is used b/c this isn't needed starting for dropdown_idx == 3
                for i in range(self.dropdown_idx[key_type] + 1, 4):
                    self.dropdown_lists[key_type][i].set('')
                    self.dropdown_lists[key_type][i].pack_forget()
                    self.dropdown_lists[key_type][i-1].set('')
            except:
                pass

    def add_shortcut(self):
        keys_from = []
        keys_to = []
        
        for i in range(0, self.dropdown_idx[0]):
            keys_from.append(self.dropdown_lists[0][i].get())
            
        for i in range(0, self.dropdown_idx[1]):
            keys_to.append(self.dropdown_lists[1][i].get())

        if not keys_from or not keys_to:
            messagebox.showwarning("Input Error", "Please select keys for both from and to combinations.")
            return

        shortcut = {
            'modifiers': keys_from[:-1],
            'key': keys_from[-1],
            'to_modifiers': keys_to[:-1],
            'to_key': keys_to[-1]
        }
        from_combination = '+'.join(keys_from)
        shortcut_remappings[from_combination] = shortcut

        remapping = f"{' + '.join(keys_from)} -> {' + '.join(keys_to)}"
        self.shortcut_mappings.append(remapping)
        self.update_shortcut_list()

    def update_shortcut_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for remapping in self.shortcut_mappings:
            ctk.CTkLabel(self.scrollable_frame, text=remapping).pack(pady=5)

    def save_shortcuts(self):
        with open(SHORTCUT_FILE, "w") as f:
            json.dump(shortcut_remappings, f)

        self.apply_shortcuts()
        messagebox.showinfo("Success", "Shortcuts saved!")

    def apply_shortcuts(self):
        for key, shortcut in shortcut_remappings.items():
            self.register_hotkey(shortcut)

    def reset_shortcuts(self):
        self.shortcut_mappings = []
        shortcut_remappings.clear()
        self.update_shortcut_list()
        messagebox.showinfo("Reset", "All shortcuts have been reset.")
        if os.path.exists(SHORTCUT_FILE):
            with open(SHORTCUT_FILE, "w") as f:
                json.dump({}, f)
        keyboard.unhook_all()

    def register_hotkey(self, shortcut):
        from_combination = '+'.join(shortcut['modifiers'] + [shortcut['key']])
        to_combination = '+'.join(shortcut['to_modifiers'] + [shortcut['to_key']])
        keyboard.remap_hotkey(from_combination, to_combination, suppress=True)
