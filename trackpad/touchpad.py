# touchpad.py
import customtkinter as ctk
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import tkinter as tk
from tkinter import messagebox
from reboot_prompt import prompt_reboot
from widgets.button import BouncingButton
from widgets.sliding_frames import SlidingFrame
from configuration_manager import ScreenInfo


class TouchpadView(SlidingFrame):
    def __init__(self, parent, controller, mode="curtains"):
        self.screen_info = ScreenInfo()
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller
        self.mode = mode

        # Mode-specific configuration
        self.configure_mode()

        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=500, height=600)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Set up UI components
        self.setup_ui()

    def configure_mode(self):
        """Configure the registry path, keys, and visual settings based on the mode."""
        self.registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        if self.mode == "curtains":
            self.curtain_keys = ['CurtainTop', 'CurtainLeft', 'CurtainRight']
            self.max_top_cm = 5
            self.max_left_right_cm = 7.5
        elif self.mode == "supercurtains":
            self.curtain_keys = ['SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight']
            self.max_top_cm = 5
            self.max_left_right_cm = 7.5
        elif self.mode == "rightclick":
            self.curtain_keys = ['RightClickZoneWidth', 'RightClickZoneHeight']
            self.max_width_cm = 7.5
            self.max_height_cm = 5
        else:
            raise ValueError("Invalid mode for TouchpadView")

        # Trackpad Image Path
        self.trackpad_img_path = os.path.join("trackpad", "gb4p16_trackpad.jpg")

        # Trackpad dimensions
        self.trackpad_width_cm = 15
        self.trackpad_height_cm = 10.7
        self.trackpad_width_px = 320
        self.trackpad_height_px = 235
        self.trackpad_x = 145
        self.trackpad_y = 245

        # Conversion factors
        self.cm_to_px_width = self.trackpad_width_px / self.trackpad_width_cm
        self.cm_to_px_height = self.trackpad_height_px / self.trackpad_height_cm

    def setup_ui(self):
        """Set up the UI components."""
        self.setup_image()
        self.create_slider_input()

        # Save button
        frame_buttons = ctk.CTkFrame(self.scrollable_frame)
        frame_buttons.pack(pady=10)
        btn_save = BouncingButton(frame_buttons, text="Save", command=self.save_values_with_prompt)
        btn_save.grid(row=0, column=0, padx=10)
        
        btn_back = BouncingButton(frame_buttons, text="Back", command=self.back_to_main_menu)
        btn_back.grid(row=0, column=1, padx=10)

    def setup_image(self):
        """Set up the trackpad image display."""
        fig, self.ax = plt.subplots(figsize=(6, 4))
        self.img = plt.imread(self.trackpad_img_path)
        self.ax.imshow(self.img)
        self.ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.canvas.get_tk_widget().pack(pady=10)

    def create_slider_input(self):
        """Create sliders and corresponding entry widgets based on the mode."""
        if self.mode == "rightclick":
            self.create_slider("Right-Click Zone Width (cm)", self.max_width_cm, "entry_width", "slider_width")
            self.create_slider("Right-Click Zone Height (cm)", self.max_height_cm, "entry_height", "slider_height")
        else:
            if(self.mode == "supercurtains"):
                self.create_slider("Top Super Curtain (Height, cm)", self.max_top_cm, "entry_top", "slider_top")
                self.create_slider("Left Super Curtain (Width, cm)", self.max_left_right_cm, "entry_left", "slider_left")
                self.create_slider("Right Super Curtain (Width, cm)", self.max_left_right_cm, "entry_right", "slider_right")
            else:
                self.create_slider("Top Curtain (Height, cm)", self.max_top_cm, "entry_top", "slider_top")
                self.create_slider("Left Curtain (Width, cm)", self.max_left_right_cm, "entry_left", "slider_left")
                self.create_slider("Right Curtain (Width, cm)", self.max_left_right_cm, "entry_right", "slider_right")

        self.initialize_slider_values()

    def create_slider(self, label_text, max_value, entry_name, slider_name):
        """Create a single slider with an entry."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text)
        label.pack(pady=5)

        slider = ctk.CTkSlider(self.scrollable_frame, from_=0, to=max_value, command=lambda value: self.update_entry_from_slider(slider, getattr(self, entry_name)))
        setattr(self, slider_name, slider)
        slider.pack(pady=5)

        entry = ctk.CTkEntry(self.scrollable_frame, justify='center')
        entry.insert(0, "0.00")
        entry.pack(pady=5)
        entry.bind("<FocusOut>", lambda event: self.on_entry_complete(entry, slider, max_value))
        entry.bind("<Return>", lambda event: self.on_entry_complete(entry, slider, max_value))
        setattr(self, entry_name, entry)

    def initialize_slider_values(self):
        """Initialize sliders with the current registry values."""
        values = self.get_current_values()
        if self.mode == "rightclick":
            self.slider_width.set(values.get('RightClickZoneWidth', 0) / 1000)
            self.slider_height.set(values.get('RightClickZoneHeight', 0) / 1000)
            
            self.update_entry_from_slider(self.slider_width, self.entry_width)
            self.update_entry_from_slider(self.slider_height, self.entry_height)
        else:
            self.slider_top.set(values.get(self.curtain_keys[0], 0) / 1000)
            self.slider_left.set(values.get(self.curtain_keys[1], 0) / 1000)
            self.slider_right.set(values.get(self.curtain_keys[2], 0) / 1000)
            
            self.update_entry_from_slider(self.slider_top, self.entry_top)
            self.update_entry_from_slider(self.slider_left, self.entry_left)
            self.update_entry_from_slider(self.slider_right, self.entry_right)

        self.update_image()

    def get_current_values(self):
        """Retrieve current registry values based on mode."""
        values = {}
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path, 0, winreg.KEY_READ)
            for key in self.curtain_keys:
                try:
                    value, _ = winreg.QueryValueEx(reg_key, key)
                    values[key] = value
                except FileNotFoundError:
                    values[key] = 0
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error reading registry values: {e}")
        return values

    def update_image(self):
        """Update the trackpad image based on slider values."""
        self.ax.clear()
        self.ax.imshow(self.img)
        self.ax.axis('off')

        if self.mode == "rightclick":
            right_click_width = float(self.entry_width.get() or 0)
            right_click_height = float(self.entry_height.get() or 0)

            # Convert cm to pixels
            right_click_width_px = right_click_width * self.cm_to_px_width
            right_click_height_px = right_click_height * self.cm_to_px_height

            # Draw non-clickable area in yellow
            rect_non_click = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, self.trackpad_height_px,
                                           linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
            self.ax.add_patch(rect_non_click)

            # Draw clickable area in green
            click_zone = plt.Rectangle((self.trackpad_x + self.trackpad_width_px - right_click_width_px,
                                        self.trackpad_y + self.trackpad_height_px - right_click_height_px),
                                       right_click_width_px, right_click_height_px,
                                       linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
            self.ax.add_patch(click_zone)
        else:
            curtain_top = float(self.entry_top.get() or 0)
            curtain_left = float(self.entry_left.get() or 0)
            curtain_right = float(self.entry_right.get() or 0)

            # Convert cm to pixels
            curtain_top_px = curtain_top * self.cm_to_px_height
            curtain_left_px = curtain_left * self.cm_to_px_width
            curtain_right_px = curtain_right * self.cm_to_px_width

            # Draw non-curtain area in yellow
            rect_non_curtain = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, self.trackpad_height_px,
                                             linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
            self.ax.add_patch(rect_non_curtain)

            # Draw left, right, and top curtains in green
            left_curtain = plt.Rectangle((self.trackpad_x, self.trackpad_y), curtain_left_px, self.trackpad_height_px,
                                         linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
            right_curtain = plt.Rectangle((self.trackpad_x + self.trackpad_width_px, self.trackpad_y), -curtain_right_px,
                                          self.trackpad_height_px, linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
            top_curtain = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, curtain_top_px,
                                        linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)

            self.ax.add_patch(left_curtain)
            self.ax.add_patch(right_curtain)
            self.ax.add_patch(top_curtain)

        self.canvas.draw()

    def update_slider_from_entry(self, entry, slider, max_value):
        """Update slider value based on entry input."""
        try:
            value = float(entry.get())
            if value > max_value:
                value = max_value
            slider.set(value)
            self.update_image()
        except ValueError:
            pass

    def update_entry_from_slider(self, slider, entry):
        """Update entry field based on slider position."""
        value = slider.get()
        entry.delete(0, "end")
        entry.insert(0, f"{value:.2f}")
        self.update_image()

    def on_entry_complete(self, entry, slider, max_value):
        """Handle completion of entry update."""
        self.update_slider_from_entry(entry, slider, max_value)
        self.format_entry(entry)

    def format_entry(self, entry):
        """Format entry to display two decimal places."""
        try:
            value = float(entry.get())
            entry.delete(0, "end")
            entry.insert(0, f"{value:.2f}")
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, "0.00")

    def save_values_with_prompt(self):
        """Prompt the user to save the registry values."""
        response = tk.messagebox.askyesno("Save Registry", "Are you sure you want to save the new registry values?\n\n")
        if response is None:  # Cancel
            return
        elif response:  # Yes, backup current values
            self.save_values()

    def save_values(self):
        """Save the values to the registry."""
        values = {
            key: int(float(getattr(self, f"entry_{key.split('Zone')[1].lower()}" if "RightClickZone" in key else key.lower()).get()) * 1000)
            for key in self.curtain_keys
        }
        self.set_values(values)
        prompt_reboot()

    def set_values(self, values):
        """Set the new values in the registry."""
        try:
            reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path)
            for key, value in values.items():
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error setting registry values: {e}")

    def back_to_main_menu(self):
        """Return to the main menu."""
        self.pack_forget()