import customtkinter as ctk
import tkinter as tk
import winreg
import os
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reboot_prompt import prompt_reboot
from PIL import Image, ImageTk
import numpy as np
from configuration_manager import ScreenInfo
import pywinstyles


class TaskbarView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.screen_info = ScreenInfo()
        
        # Scrollable frame for taskbar settings
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=500, height=600)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Registry paths and keys for taskbar settings
        self.registry_path_advanced = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
        self.registry_path_stuckrects = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3'

        # Construct paths relative to the current script's directory
        base_dir = os.path.dirname(__file__)
        self.background_img_path = os.path.join(base_dir, "background_image.png")
        self.taskbar_img_path = os.path.join(base_dir, "taskbar.png")
        
        # Max values for sliders
        self.max_taskbar_size = 100.0  # Taskbar length max value
        self.max_taskbar_transparency = 100.0  # Transparency max value

        self.taskbar_positions = {"Bottom": 0x03, "Top": 0x01}
        self.auto_hide_options = {"Disabled": 0x03, "Enabled": 0x02}
        self.icon_size_options = {"Large": 0, "Small": 1}
        self.alignment_options = {"Center": 1, "Left": 0}  # Windows 11 only
        self.clock_visibility_options = {"Show": 1, "Hide": 0}
        self.label_visibility_options = {"Always Combine, Hide Labels": 0, "Combine Only When Taskbar Is Full": 1, "Never Combine": 2}
        self.thumbnail_size_options = [str(i) for i in range(100, 301, 50)]  # From 100px to 300px in steps of 50px

        # Setup UI
        self.setup_ui()
        
        current_values = self.get_current_taskbar_values()
        
        self.update_ui_from_values(current_values)

    def setup_ui(self):
        
        self.setup_image()
        # Create taskbar length slider and entry
        self.create_slider("Taskbar Length", self.max_taskbar_size, "entry_taskbar_length", "slider_taskbar_length")
        
        # Create taskbar transparency slider and entry
        self.create_slider("Taskbar Transparency", self.max_taskbar_transparency, "entry_taskbar_transparency", "slider_taskbar_transparency")

        # Create dropdowns for taskbar position and auto-hide
        # Create taskbar position dropdown
        self.create_dropdown("Taskbar Position", self.taskbar_positions, "position_var", "position_dropdown", "position_dropdown")
        self.create_dropdown("Auto-Hide Taskbar", self.auto_hide_options, "auto_hide_var", "auto_hide_dropdown", "auto_hide_dropdown")
        self.create_dropdown("Taskbar Icon Size", self.icon_size_options, "icon_size_var", "icon_size_dropdown", "icon_size_dropdown")
        self.create_dropdown("Taskbar Alignment", self.alignment_options, "alignment_var", "alignment_dropdown", "alignment_dropdown")
        self.create_dropdown("Taskbar Clock", self.clock_visibility_options, "clock_var", "clock_dropdown", "clock_dropdown")
        self.create_dropdown("Taskbar Labels", self.label_visibility_options, "label_var", "label_dropdown", "label_dropdown")
        self.create_dropdown("Thumbnail Preview Size (px)", self.thumbnail_size_options, "thumbnail_var", "thumbnail_dropdown", "thumbnail_dropdown")


        # Save button
        frame_buttons = ctk.CTkFrame(self.scrollable_frame)
        frame_buttons.pack(pady=10)

        btn_save = ctk.CTkButton(frame_buttons, text="Save", command=self.save_taskbar_values_with_prompt)
        btn_save.pack(pady=5)

    def update_ui_from_values(self, values):
        """Update the UI elements with the values from the registry."""
        # Update taskbar length slider
        self.slider_taskbar_length.set(values.get("TaskbarLength", self.max_taskbar_size))
        self.entry_taskbar_length.delete(0, "end")
        self.entry_taskbar_length.insert(0, f"{values.get('TaskbarLength', self.max_taskbar_size):.2f}")

        # Update taskbar transparency slider
        self.slider_taskbar_transparency.set(values.get("TaskbarTransparency", self.max_taskbar_transparency))
        self.entry_taskbar_transparency.delete(0, "end")
        self.entry_taskbar_transparency.insert(0, f"{values.get('TaskbarTransparency', self.max_taskbar_transparency):.2f}")

        # Update dropdowns
        self.position_var.set("Top" if values.get("Position") == 0x01 else "Bottom")
        self.auto_hide_var.set("Enabled" if values.get("AutoHide") == 0x02 else "Disabled")
        self.icon_size_var.set("Small" if values.get("TaskbarSmallIcons") == 1 else "Large")
        self.alignment_var.set("Left" if values.get("TaskbarAlignment") == 0 else "Center")  # Windows 11 alignment
        self.clock_var.set("Hide" if values.get("ShowClock") == 0 else "Show")

        # Handle Taskbar Label Visibility
        label_visibility_mapping = {0: "Always Combine, Hide Labels", 1: "Combine Only When Taskbar Is Full", 2: "Never Combine"}
        taskbar_glom_level = values.get("TaskbarGlomLevel", 0)
        self.label_var.set(label_visibility_mapping.get(taskbar_glom_level, "Always Combine, Hide Labels"))

        # Handle Thumbnail Preview Size
        self.thumbnail_var.set(str(values.get("MinThumbSizePx", 100)))  # Thumbnail preview size

    def setup_image(self):
        """Load and display the background and taskbar images with CTkImage."""

        # Calculate dimensions for the background image dynamically
        image_width = self.screen_info.window_width
        background_image_width = int(self.screen_info.window_width * 0.8)  # Ensure this is an integer
        screen_ratio = self.screen_info.screen_width / self.screen_info.screen_height
        background_image_height = int(background_image_width / screen_ratio)  # Ensure this is an integer

        taskbar_ratio = 40.55  # width is 40.55 times larger than height
        taskbar_width = background_image_width
        taskbar_height = int(taskbar_width / taskbar_ratio)  # Ensure this is an integer

        # Load and resize background image
        self.background_image = Image.open(self.background_img_path)
        self.background_image_resized = self.background_image.resize((background_image_width, background_image_height), Image.Resampling.LANCZOS)  # Resize to fit
        self.background_image_ctk = ctk.CTkImage(self.background_image_resized, size=(background_image_width, background_image_height))  # Convert to CTkImage

        # Load and resize taskbar image
        self.taskbar_image = Image.open(self.taskbar_img_path)
        self.taskbar_image_resized = self.taskbar_image.resize((taskbar_width, taskbar_height), Image.Resampling.LANCZOS)  # Resize to fit at bottom
        self.taskbar_image_ctk = ctk.CTkImage(self.taskbar_image_resized, size=(taskbar_width, taskbar_height))  # Convert to CTkImage

        # Create and place background image label
        self.label_background_img = ctk.CTkLabel(self.scrollable_frame, image=self.background_image_ctk, text="", width=background_image_width, height=background_image_height)
        self.label_background_img.pack()
        
        # Create and place taskbar image label
        self.xa = (image_width - taskbar_width) // 2 - 10 # Center the taskbar image
        self.label_taskbar_img = ctk.CTkLabel(self.scrollable_frame, image=self.taskbar_image_ctk, text="", width=taskbar_width, height=taskbar_height, fg_color="transparent")
        self.label_taskbar_img.place(x = self.xa, y=background_image_height - taskbar_height)  # Adjust position to overlay at bottom of the background image

        self.label_height_position = background_image_height - taskbar_height

    def update_image(self, source=None):
        """Updates the taskbar overlay on the background based on the user inputs for position, length, and transparency."""

        if source:
            # Initialize variables to store current states if they don't exist
            if not hasattr(self, 'current_width'):
                self.current_width = self.taskbar_image_resized.width
            if not hasattr(self, 'current_height'):
                self.current_height = self.taskbar_image_resized.height
            if not hasattr(self, 'current_transparency'):
                self.current_transparency = 255  # Default transparency value (fully opaque)
            if not hasattr(self, 'label_position'):
                self.label_position = self.background_image_resized.height - self.current_height  # Default to bottom position

            # Only update the relevant value based on the source
            if source == "slider_taskbar_length" or source == "entry_taskbar_length":
                # Calculate new taskbar width based on the slider value
                self.current_width = int((self.screen_info.window_width * 0.8) / 100 * self.slider_taskbar_length.get())

            elif source == "slider_taskbar_transparency" or source == "entry_taskbar_transparency":
                # Calculate and store the transparency value
                self.current_transparency = int(255 * (self.slider_taskbar_transparency.get() / self.max_taskbar_transparency))  # Alpha value (0-255)

            elif source == "position_dropdown":
                # Set the taskbar position based on dropdown selection
                if self.position_var.get() == "Top":
                    self.label_position = 0  # Move to top of the background image
                else:  # Default to bottom position
                    self.label_position = self.background_image_resized.height - self.current_height

            # Apply the updates to the image and label at the end
            # 1. Resize the taskbar image based on the current width and height
            self.taskbar_image_resized = self.taskbar_image.resize((self.current_width, self.current_height), Image.Resampling.LANCZOS)

            # 2. Apply the current transparency to the taskbar image
            taskbar_rgba = self.taskbar_image_resized.convert("RGBA")
            data = np.array(taskbar_rgba)
            #data[:, :, 3] = self.current_transparency  # Modify the alpha channel
            self.taskbar_image_resized = Image.fromarray(data)

            # 3. Convert to a CTkImage and update the label image
            self.taskbar_image_ctk = ctk.CTkImage(self.taskbar_image_resized, size=(self.current_width, self.current_height))
            self.label_taskbar_img.configure(image=self.taskbar_image_ctk, width=self.current_width, height=self.current_height, fg_color="transparent")

            # 4. Position the label based on the updated x and y values
            self.xa = (self.screen_info.window_width - self.current_width) // 2 - 10
            self.label_taskbar_img.place(x=self.xa, y=self.label_position)

            # Should probably update the code so that there are less burdon on the cpu
            # Update required so that the taskbar transparency is shown

            pywinstyles.set_opacity(self.label_taskbar_img.winfo_id(), self.current_transparency)

    def create_slider(self, label_text, max_value, entry_name, slider_name):
        """Create a slider and an entry that are synchronized."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text)
        label.pack(pady=5)

        # Create the slider
        slider = ctk.CTkSlider(self.scrollable_frame, from_=0, to=max_value, command=lambda value: [self.update_entry_from_slider(slider, getattr(self, entry_name)), self.update_image(slider_name)])
        slider.pack(pady=5)
        slider.set(max_value) # Default value should be set to the CURRENT VALUE - To be updated
        setattr(self, slider_name, slider)

        # Create the entry
        entry = ctk.CTkEntry(self.scrollable_frame, justify='center')
        entry.insert(0, f"{max_value:.2f}")
        entry.pack(pady=5)
        entry.bind("<FocusOut>", lambda event: [self.on_entry_complete(entry, slider, max_value), self.update_image(entry_name)])
        entry.bind("<Return>", lambda event: [self.on_entry_complete(entry, slider, max_value), self.update_image(entry_name)])
        setattr(self, entry_name, entry)

    def create_dropdown(self, label_text, values, var_name, dropdown_name, source):
        """Create a dropdown menu with the specified values."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text)
        label.pack(pady=5)

        # Handle if values is a list or a dictionary
        if isinstance(values, dict):
            value_list = list(values.keys())  # Use keys if it's a dictionary
        elif isinstance(values, list):
            value_list = values  # Use the list directly if it's a list
        else:
            raise TypeError("Values must be a dictionary or a list.")

        var = tk.StringVar()
        dropdown = ctk.CTkComboBox(self.scrollable_frame, values=value_list, variable=var)
        dropdown.pack(pady=5)
        dropdown.set(value_list[0])  # Set default value
        setattr(self, var_name, var)
        setattr(self, dropdown_name, dropdown)

        # Trigger update_image when the dropdown value changes
        var.trace_add('write', lambda *args: self.update_image(source))

    def update_slider_from_entry(self, entry, slider, max_value):
        """Update the slider when the entry value is changed."""
        try:
            value = float(entry.get())
            if value > max_value:
                value = max_value
            slider.set(value)
        except ValueError:
            pass

    def update_entry_from_slider(self, slider, entry):
        """Update the entry when the slider value is changed."""
        value = slider.get()
        entry.delete(0, "end")
        entry.insert(0, f"{value:.2f}")

    def on_entry_complete(self, entry, slider, max_value):
        """Handle entry validation and update the slider accordingly."""
        self.update_slider_from_entry(entry, slider, max_value)
        self.format_entry(entry)

    def format_entry(self, entry):
        """Format the entry value."""
        try:
            value = float(entry.get())
            entry.delete(0, "end")
            entry.insert(0, f"{value:.2f}")
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, "0.00")

    def save_taskbar_values_with_prompt(self):
        # Prompt user before saving
        response = tk.messagebox.askyesno(
            "Save Taskbar Settings",
            "Are you sure you want to save the new taskbar settings?"
        )

        if response is None:  # Cancel
            return
        elif response:  # Yes, save values
            self.save_taskbar_values()

    def save_taskbar_values(self):
        """Save the current taskbar values to the Windows registry and apply changes."""
        # Get selected values from UI components
        taskbar_length_value = float(self.entry_taskbar_length.get())
        taskbar_transparency_value = float(self.entry_taskbar_transparency.get())
        position_value = self.taskbar_positions[self.position_var.get()]
        auto_hide_value = self.auto_hide_options[self.auto_hide_var.get()]

        # Retrieve values from new dropdowns
        taskbar_icon_size = self.icon_size_options[self.icon_size_var.get()]
        taskbar_alignment = self.alignment_options[self.alignment_var.get()]  # Only applies to Windows 11
        taskbar_clock = self.clock_visibility_options[self.clock_var.get()]
        taskbar_labels = self.label_visibility_options[self.label_var.get()]
        taskbar_thumbnail_size = int(self.thumbnail_var.get())  # Thumbnail size is stored as an integer

        try:
            # Save taskbar position and auto-hide settings
            reg_key_stuckrects = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_stuckrects, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            value, regtype = winreg.QueryValueEx(reg_key_stuckrects, "Settings")
            value_list = list(value)

            # Modify the taskbar position and auto-hide options in the registry
            value_list[8] = auto_hide_value  # Auto-hide: byte 8
            value_list[12] = position_value  # Taskbar position: byte 12

            # Save modified settings
            winreg.SetValueEx(reg_key_stuckrects, "Settings", 0, regtype, bytes(value_list))
            winreg.CloseKey(reg_key_stuckrects)

            # Save taskbar advanced options
            reg_key_advanced = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_advanced, 0, winreg.KEY_SET_VALUE)
            
            # Save taskbar icon size (small/large icons)
            winreg.SetValueEx(reg_key_advanced, "TaskbarSmallIcons", 0, winreg.REG_DWORD, taskbar_icon_size)
            
            # Save taskbar alignment (only effective in Windows 11)
            winreg.SetValueEx(reg_key_advanced, "TaskbarAl", 0, winreg.REG_DWORD, taskbar_alignment)
            
            # Save taskbar clock visibility
            winreg.SetValueEx(reg_key_advanced, "ShowClock", 0, winreg.REG_DWORD, taskbar_clock)
            
            # Save taskbar label visibility
            winreg.SetValueEx(reg_key_advanced, "TaskbarGlomLevel", 0, winreg.REG_DWORD, taskbar_labels)
            
            winreg.CloseKey(reg_key_advanced)

            # Save taskbar thumbnail preview size
            reg_key_taskband = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_taskband, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key_taskband, "MinThumbSizePx", 0, winreg.REG_DWORD, taskbar_thumbnail_size)
            winreg.CloseKey(reg_key_taskband)

            # Restart Explorer to apply the changes
            os.system("taskkill /f /im explorer.exe & start explorer.exe")

            # Display success message
            print("Taskbar settings have been successfully updated and applied.")
            messagebox.showinfo("Success", "Taskbar settings have been successfully updated. Explorer will restart to apply the changes.")
            
        except Exception as e:
            print(f"Error saving taskbar settings: {e}")
            messagebox.showerror("Error", f"Error saving taskbar settings: {e}")

    def get_current_taskbar_values(self):
        """Read taskbar size, position, auto-hide, and other settings from the registry."""
        taskbar_values = {
            "AutoHide": None,
            "Position": None,
            "TaskbarSmallIcons": None,
            "TaskbarAlignment": None,
            "ShowClock": None,
            "TaskbarGlomLevel": None,
            "MinThumbSizePx": None,
            "TaskbarTransparency": 100.0
        }

        try:
            # Retrieve taskbar position and auto-hide from the "StuckRects3" registry key
            reg_key_stuckrects = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_stuckrects, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(reg_key_stuckrects, "Settings")
            taskbar_values["AutoHide"] = value[8]  # Byte 8 for auto-hide setting
            taskbar_values["Position"] = value[12]  # Byte 12 for position setting
            winreg.CloseKey(reg_key_stuckrects)

        except FileNotFoundError:
            print(f"Error: 'StuckRects3' registry key not found.")
        except Exception as e:
            print(f"Error reading registry values from StuckRects3: {e}")

        try:
            # Retrieve taskbar advanced settings (icon size, alignment, clock, labels) from "Advanced" registry key
            reg_key_advanced = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_advanced, 0, winreg.KEY_READ)
            taskbar_values["TaskbarSmallIcons"], _ = winreg.QueryValueEx(reg_key_advanced, "TaskbarSmallIcons")
            taskbar_values["TaskbarAlignment"], _ = winreg.QueryValueEx(reg_key_advanced, "TaskbarAl")  # Alignment (Windows 11)
            taskbar_values["ShowClock"], _ = winreg.QueryValueEx(reg_key_advanced, "ShowClock")
            taskbar_values["TaskbarGlomLevel"], _ = winreg.QueryValueEx(reg_key_advanced, "TaskbarGlomLevel")  # Labels visibility
            winreg.CloseKey(reg_key_advanced)

        except FileNotFoundError:
            print(f"Error: 'Advanced' registry key not found.")
        except Exception as e:
            print(f"Error reading registry values from Advanced: {e}")

        try:
            # Retrieve thumbnail preview size from "Taskband" registry key
            reg_key_taskband = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_taskband, 0, winreg.KEY_READ)
            taskbar_values["MinThumbSizePx"], _ = winreg.QueryValueEx(reg_key_taskband, "MinThumbSizePx")  # Thumbnail preview size
            winreg.CloseKey(reg_key_taskband)

        except FileNotFoundError:
            print(f"Error: 'Taskband' registry key not found.")
        except Exception as e:
            print(f"Error reading registry values from Taskband: {e}")

        return taskbar_values

