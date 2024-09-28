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

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        
        self.setup_image()
        # Create taskbar length slider and entry
        self.create_slider("Taskbar Length", self.max_taskbar_size, "entry_taskbar_length", "slider_taskbar_length")


        # Create taskbar transparency slider and entry
        self.create_slider("Taskbar Transparency", self.max_taskbar_transparency, "entry_taskbar_transparency", "slider_taskbar_transparency")

        # Create dropdowns for taskbar position and auto-hide
        self.create_position_dropdown()
        self.create_auto_hide_dropdown()

        # Save button
        frame_buttons = ctk.CTkFrame(self.scrollable_frame)
        frame_buttons.pack(pady=10)

        btn_save = ctk.CTkButton(frame_buttons, text="Save", command=self.save_taskbar_values_with_prompt)
        btn_save.pack(pady=5)

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
            print(f"Updating image based on {source}")

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
                print(f"Taskbar length: {self.slider_taskbar_length.get()}")

                # Calculate new taskbar width based on the slider value
                self.current_width = int((self.screen_info.window_width * 0.8) / 100 * self.slider_taskbar_length.get())

            elif source == "slider_taskbar_transparency" or source == "entry_taskbar_transparency":
                print(f"Taskbar transparency: {self.slider_taskbar_transparency.get()}")

                # Calculate and store the transparency value
                self.current_transparency = int(255 * (self.slider_taskbar_transparency.get() / self.max_taskbar_transparency))  # Alpha value (0-255)

            elif source == "position_dropdown":
                print(f"Taskbar position: {self.position_var.get()}")

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
            data[:, :, 3] = self.current_transparency  # Modify the alpha channel
            self.taskbar_image_resized = Image.fromarray(data)

            # 3. Convert to a CTkImage and update the label image
            self.taskbar_image_ctk = ctk.CTkImage(self.taskbar_image_resized, size=(self.current_width, self.current_height))
            self.label_taskbar_img.configure(image=self.taskbar_image_ctk, width=self.current_width, height=self.current_height, fg_color="transparent")

            # 4. Position the label based on the updated x and y values
            self.xa = (self.screen_info.window_width - self.current_width) // 2 - 10
            self.label_taskbar_img.place(x=self.xa, y=self.label_position)

            # Should probably update the code so that there are less burdon on the cpu
            # Update required so that the taskbar transparency is shown

    def create_slider(self, label_text, max_value, entry_name, slider_name):
        """Create a slider and an entry that are synchronized."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text)
        label.pack(pady=5)

        # Create the slider
        slider = ctk.CTkSlider(self.scrollable_frame, from_=0, to=max_value, command=lambda value: [self.update_entry_from_slider(slider, getattr(self, entry_name)), self.update_image(slider_name)])
        slider.pack(pady=5)
        slider.set(0) # Default value should be set to the CURRENT VALUE - To be updated
        setattr(self, slider_name, slider)

        # Create the entry
        entry = ctk.CTkEntry(self.scrollable_frame, justify='center')
        entry.insert(0, "0.00") # Entry should also be set to current value
        entry.pack(pady=5)
        entry.bind("<FocusOut>", lambda event: [self.on_entry_complete(entry, slider, max_value), self.update_image(entry_name)])
        entry.bind("<Return>", lambda event: [self.on_entry_complete(entry, slider, max_value), self.update_image(entry_name)])
        setattr(self, entry_name, entry)

    def create_position_dropdown(self):
        # Taskbar position selection
        label = ctk.CTkLabel(self.scrollable_frame, text="Taskbar Position")
        label.pack(pady=5)

        self.position_var = tk.StringVar()
        dropdown = ctk.CTkComboBox(self.scrollable_frame, values=list(self.taskbar_positions.keys()), variable=self.position_var)
        dropdown.pack(pady=5)
        dropdown.set("Bottom")  # Default value

        # Trigger update_image when the position changes
        self.position_var.trace_add('write', lambda *args: self.update_image("position_dropdown"))


    def create_auto_hide_dropdown(self):
        # Auto-hide taskbar selection
        label = ctk.CTkLabel(self.scrollable_frame, text="Auto-Hide Taskbar")
        label.pack(pady=5)

        self.auto_hide_var = tk.StringVar()
        dropdown = ctk.CTkComboBox(self.scrollable_frame, values=list(self.auto_hide_options.keys()), variable=self.auto_hide_var)
        dropdown.pack(pady=5)
        dropdown.set("Disabled")  # Default value
        
        self.auto_hide_var.trace_add('write', lambda *args: self.update_image("auto_hide_dropdown"))

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
        # Get selected values
        taskbar_length_value = float(self.entry_taskbar_length.get())
        taskbar_transparency_value = float(self.entry_taskbar_transparency.get())
        position_value = self.taskbar_positions[self.position_var.get()]
        auto_hide_value = self.auto_hide_options[self.auto_hide_var.get()]

        # Save taskbar length and transparency to registry (if applicable)
        # Modify the registry accordingly based on your requirements for taskbar length and transparency.
        # These are just placeholder values, as Windows registry doesn't directly control length/transparency.

        # Save taskbar position and auto-hide to registry
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_stuckrects, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            value, regtype = winreg.QueryValueEx(reg_key, "Settings")
            value_list = list(value)

            # Modify the taskbar position and auto-hide options in the registry
            value_list[8] = auto_hide_value  # Auto-hide: byte 8
            value_list[12] = position_value  # Taskbar position: byte 12

            # Save modified settings
            winreg.SetValueEx(reg_key, "Settings", 0, regtype, bytes(value_list))
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error saving taskbar position/auto-hide: {e}")

        # Prompt user to restart Explorer to apply changes
        prompt_reboot()

    def get_current_taskbar_values(self):
        """Read taskbar size, position, and auto-hide settings from registry."""
        taskbar_values = {}
        try:
            # Taskbar position and auto-hide
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path_stuckrects, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(reg_key, "Settings")
            taskbar_values["AutoHide"] = value[8]
            taskbar_values["Position"] = value[12]
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error reading registry values: {e}")
        return taskbar_values
