import customtkinter as ctk
import tkinter as tk
import winreg
import os
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reboot_prompt import prompt_reboot
from PIL import Image, ImageEnhance
import numpy as np


class TaskbarView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
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
        self.max_taskbar_size = 10.0  # Taskbar length max value
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
        # Create a figure for displaying the images
        fig, self.ax = plt.subplots(figsize=(6, 4))

        # Check if the background image path exists
        if not os.path.exists(self.background_img_path):
            print(f"Error: Background image not found at {self.background_img_path}")
            return

        # Check if the taskbar image path exists
        if not os.path.exists(self.taskbar_img_path):
            print(f"Error: Taskbar image not found at {self.taskbar_img_path}")
            return

        # Load the background and taskbar images using plt.imread
        self.background_image = plt.imread(self.background_img_path)  # Load background image
        self.taskbar_image = plt.imread(self.taskbar_img_path)  # Load taskbar image

        # Get dimensions of the images
        background_height, background_width, _ = self.background_image.shape
        taskbar_height, taskbar_width, _ = self.taskbar_image.shape

        # Resize taskbar to match the background width (proportionally scale)
        scaling_factor = background_width / taskbar_width
        taskbar_resized_height = int(taskbar_height * scaling_factor)
        taskbar_resized = Image.fromarray((self.taskbar_image * 255).astype(np.uint8))
        taskbar_resized = taskbar_resized.resize((background_width, taskbar_resized_height), Image.Resampling.LANCZOS)
        self.taskbar_image_resized = np.array(taskbar_resized) / 255.0  # Convert back to numpy array (normalize)

        # Display the background image first
        self.ax.imshow(self.background_image, extent=[0, background_width, 0, background_height], zorder=0)  # Background image

        # Initial position for the taskbar (bottom of the background)
        self.taskbar_y_position = 0  # Start at bottom of the plot
        self.taskbar_x_position = 0  # Align taskbar with the left edge of the background

        # Display the taskbar image on top of the background
        self.ax.imshow(self.taskbar_image_resized, extent=[self.taskbar_x_position, background_width,
                                                        self.taskbar_y_position, taskbar_resized_height], zorder=1)

        # Hide the axes for a clean display
        self.ax.axis('off')

        # Embed the matplotlib figure into the tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.canvas.get_tk_widget().pack(pady=10)


    def update_image(self, source=None):
        """Updates the taskbar overlay on the background based on the user inputs for position, length, and transparency."""

        if source:
            print(f"Updating image based on {source}")

            if source == "slider_taskbar_length" or source == "entry_taskbar_length":
                print(f"Taskbar length: {self.slider_taskbar_length.get()}")
                
            elif source == "slider_taskbar_transparency" or source == "entry_taskbar_transparency":
                print(f"Taskbar transparency: {self.slider_taskbar_transparency.get()}")
            
            elif source == "position_dropdown":
                print(f"Taskbar position: {self.position_var.get()}")
            
            elif source == "auto_hide_dropdown":
                print(f"Auto-hide taskbar: {self.auto_hide_var.get()}")
            
            else:
                print("Unknown source")

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
