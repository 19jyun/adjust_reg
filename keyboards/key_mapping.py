import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from reboot_prompt import prompt_reboot
import winreg
from widgets.button import BouncingButton
from widgets.sliding_frames import SlidingFrame
from configuration_manager import ScreenInfo

class KeyRemapView(SlidingFrame):
    def __init__(self, parent, controller):
        self.screen_info = ScreenInfo()
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller

        self.available_keys = {
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

        # Store the remapped keys
        self.remapped_keys = []

        # Layout
        self.setup_ui()

    def setup_ui(self):
        # Dropdowns for key selection
        ctk.CTkLabel(self, text="Select Key to Remap:").pack(pady=5)
        self.key_from_var = tk.StringVar()
        self.key_from_dropdown = ctk.CTkComboBox(self, variable=self.key_from_var, values=list(self.available_keys.keys()))
        self.key_from_dropdown.pack(pady=5)

        ctk.CTkLabel(self, text="Select Key to Remap To:").pack(pady=5)
        self.key_to_var = tk.StringVar()
        self.key_to_dropdown = ctk.CTkComboBox(self, variable=self.key_to_var, values=list(self.available_keys.keys()))
        self.key_to_dropdown.pack(pady=5)

        # Add button
        BouncingButton(self, text="Add Remapping", command=self.add_remapping).pack(pady=10)

        # Scrollable frame to display remapped keys
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scrollable_frame.pack(pady=10)

        self.get_remapped_list() #retrieves the remapped keys from the registry and updates the list

        # Save and Reset buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        BouncingButton(button_frame, text="Save Mappings", command=self.save_mappings).grid(row=0, column=0, padx=10)
        BouncingButton(button_frame, text="Reset", command=self.reset_mappings).grid(row=0, column=1, padx=10)

        # List to display the current remappings
        self.update_remapped_list()

    def add_remapping(self):
        key_from = self.key_from_var.get()
        key_to = self.key_to_var.get()

        if not key_from or not key_to:
            messagebox.showwarning("Input Error", "Please select both keys.")
            return

        # Add the remapping to the list
        remapping = f"{key_from} -> {key_to}"
        self.remapped_keys.append(remapping)
        self.update_remapped_list()

    def update_remapped_list(self):
        # Clear the current list in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Display each remapped key
        for remapping in self.remapped_keys:
            ctk.CTkLabel(self.scrollable_frame, text=remapping).pack(pady=5)

    def save_mappings(self):
        try:
            reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Keyboard Layout")
            scancode_map = self.generate_scancode_map()
            winreg.SetValueEx(reg_key, "Scancode Map", 0, winreg.REG_BINARY, scancode_map)
            winreg.CloseKey(reg_key)
            
            prompt_reboot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save remappings: {e}")

    def generate_scancode_map(self):
        # Initialize the scancode map structure
        mappings = []
        for remapping in self.remapped_keys:
            key_from, key_to = remapping.split(" -> ")
            key_from_scancode = self.available_keys[key_from]
            key_to_scancode = self.available_keys[key_to]
            mappings.append((key_to_scancode, key_from_scancode))

        # The scancode map format:
        # - Header: 8 bytes
        # - Number of mappings + 1 (for null entry) (4 bytes)
        # - Mappings: 4 bytes each (target, source) per entry
        # - Footer: 4 bytes (null mapping)
        num_mappings = len(mappings) + 1
        header = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        body = b"".join([key_to.to_bytes(2, 'little') + key_from.to_bytes(2, 'little') for key_to, key_from in mappings])
        footer = b"\x00\x00\x00\x00"
        return header + num_mappings.to_bytes(4, 'little') + body + footer

    def reset_mappings(self):

        response = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the Key mappings? This will delete the scancode map. This decision is irreversible.")
        
        if response:
            try:
                self.remapped_keys = []
                self.update_remapped_list()
                
                # Remove the Scancode Map from the registry
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Keyboard Layout", 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(reg_key, "Scancode Map")
                winreg.CloseKey(reg_key)

                # Inform the user that the mappings have been reset
                prompt_reboot()
                            
            except FileNotFoundError: #No remapping information at the first place
                print("No remapping found in the registry.")
            except Exception as e:
                print(f"Failed to delete Scancode Map from registry")

    def get_remapped_list(self):
        try:
            # Open the registry key
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Keyboard Layout", 0, winreg.KEY_READ)

            # Try to read the Scancode Map value
            scancode_map, _ = winreg.QueryValueEx(reg_key, "Scancode Map")
            winreg.CloseKey(reg_key)

            # Decode the scancode map
            if scancode_map:
                self.decode_and_update_remapped_keys(scancode_map)

        except FileNotFoundError:
            print("No remapping found in the registry.")
        except Exception as e:
            print(f"Failed to read Scancode Map from registry: {e}")

    def decode_and_update_remapped_keys(self, scancode_map):
        if not scancode_map or len(scancode_map) < 12:
            return

        self.remapped_keys = []  # Reset the remapped keys list
        mappings = []

        # Number of mappings + 1 (the last 4 bytes are null, indicating the end)
        num_mappings = int.from_bytes(scancode_map[8:12], byteorder='little') - 1

        # Each mapping consists of 4 bytes (new key, old key)
        for i in range(num_mappings):
            offset = 12 + i * 4
            new_key = int.from_bytes(scancode_map[offset:offset + 2], byteorder='little')
            old_key = int.from_bytes(scancode_map[offset + 2:offset + 4], byteorder='little')

            # Find the corresponding key names using the self.available_keys dictionary
            old_key_name = self.get_key_name_by_scancode(old_key)
            new_key_name = self.get_key_name_by_scancode(new_key)

            # If both keys are valid, add the remapping to the list
            if old_key_name and new_key_name:
                remapping = f"{old_key_name} -> {new_key_name}"
                self.remapped_keys.append(remapping)

        # Update the UI with the remapped keys
        self.update_remapped_list()

    def get_key_name_by_scancode(self, scancode):
        # Search the available_keys dictionary to find the key by its scancode
        for key_name, key_scancode in self.available_keys.items():
            if key_scancode == scancode:
                return key_name
        return None