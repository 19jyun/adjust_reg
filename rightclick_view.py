import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from new_ui_style import NewUIStyle
from backup_view import BackupView
from reboot_prompt import prompt_reboot

class RightClickView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ui_style = NewUIStyle(NewUIStyle.get_scaling_factor())
        
        # Registry keys and image paths
        self.registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        self.right_click_keys = ['RightClickZoneWidth', 'RightClickZoneHeight']
        self.trackpad_img_path = "trackpad/gb4p16_trackpad.jpg"
        
        # Trackpad dimensions
        self.trackpad_width_cm = 15
        self.trackpad_height_cm = 10.7
        self.trackpad_width_px = 320
        self.trackpad_height_px = 235
        self.trackpad_x = 145
        self.trackpad_y = 245
        self.max_width_cm = 7.5
        self.max_height_cm = 5
        
        self.cm_to_px_width = self.trackpad_width_px / self.trackpad_width_cm
        self.cm_to_px_height = self.trackpad_height_px / self.trackpad_height_cm
        
        self.setup_ui()

    def setup_ui(self):
        # UI Padding and Image
        padding_x, padding_y = self.ui_style.get_padding()
        self.setup_image(padding_x, padding_y)

        # Sliders and entries
        self.create_slider_input(padding_x, padding_y)

        # Save and Back buttons
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=padding_y)

        btn_save = tk.Button(frame_buttons, text="Save", command=self.save_right_click_values_with_prompt)
        self.ui_style.apply_button_style(btn_save)
        btn_save.grid(row=0, column=0, padx=padding_x)

        btn_back = tk.Button(frame_buttons, text="Back", command=lambda: self.controller.show_frame("MainMenu"))
        self.ui_style.apply_button_style(btn_back)
        btn_back.grid(row=0, column=1, padx=padding_x)

    def setup_image(self, padding_x, padding_y):
        fig, self.ax = plt.subplots(figsize=((self.ui_style.window_width / self.ui_style.scale_factor) / 180,
                                             (self.ui_style.window_height / self.ui_style.scale_factor) / 250))
        self.img = plt.imread(self.trackpad_img_path)
        self.ax.imshow(self.img, aspect='auto')
        self.ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0, wspace=0)
        self.ax.set_position([0, 0, 1, 1])

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(padx=padding_x, pady=padding_y)

    def create_slider_input(self, padding_x, padding_y):
        self.create_slider("Right-Click Zone Width (cm)", self.max_width_cm, "entry_width", "slider_width", padding_y)
        self.create_slider("Right-Click Zone Height (cm)", self.max_height_cm, "entry_height", "slider_height", padding_y)

        self.initialize_slider_values()

    def create_slider(self, label_text, max_value, entry_name, slider_name, padding_y):
        label = tk.Label(self, text=label_text)
        self.ui_style.apply_label_style(label)
        label.pack(pady=padding_y)

        slider = ttk.Scale(self, from_=0, to=max_value, orient='horizontal', length=self.ui_style.slider_length,
                           command=lambda x: self.update_entry_from_slider(slider, getattr(self, entry_name)))
        setattr(self, slider_name, slider)
        slider.pack(pady=padding_y)

        entry = tk.Entry(self, justify='center')
        self.ui_style.apply_entry_style(entry)
        entry.insert(0, "0.00")
        entry.pack(pady=padding_y)
        entry.bind("<FocusOut>", lambda event: self.on_entry_complete(entry, slider, max_value))
        entry.bind("<Return>", lambda event: self.on_entry_complete(entry, slider, max_value))
        setattr(self, entry_name, entry)

    def initialize_slider_values(self):
        right_click_values = self.get_current_right_click_values()
        self.slider_width.set(right_click_values.get('RightClickZoneWidth', 0) / 1000)
        self.slider_height.set(right_click_values.get('RightClickZoneHeight', 0) / 1000)

    def get_current_right_click_values(self):
        right_click_values = {}
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path, 0, winreg.KEY_READ)
            for key in self.right_click_keys:
                try:
                    value, _ = winreg.QueryValueEx(reg_key, key)
                    right_click_values[key] = value
                except FileNotFoundError:
                    right_click_values[key] = 0
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error reading registry values: {e}")
        return right_click_values

    def set_right_click_values(self, right_click_values):
        try:
            reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path)
            for key, value in right_click_values.items():
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error setting registry values: {e}")

    def update_image(self):
        self.ax.clear()
        self.ax.imshow(self.img)

        right_click_width = float(self.entry_width.get())
        right_click_height = float(self.entry_height.get())

        right_click_width_px = right_click_width * self.cm_to_px_width
        right_click_height_px = right_click_height * self.cm_to_px_height

        rect_non_click = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, self.trackpad_height_px,
                                       linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
        self.ax.add_patch(rect_non_click)

        click_zone = plt.Rectangle((self.trackpad_x + self.trackpad_width_px - right_click_width_px,
                                    self.trackpad_y + self.trackpad_height_px - right_click_height_px),
                                   right_click_width_px, right_click_height_px,
                                   linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)

        self.ax.add_patch(click_zone)
        self.canvas.draw()

    def update_slider_from_entry(self, entry, slider, max_value):
        try:
            value = float(entry.get())
            if value > max_value:
                value = max_value
            slider.set(value)
            self.update_image()
        except ValueError:
            pass

    def update_entry_from_slider(self, slider, entry):
        value = slider.get()
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:.2f}")
        self.update_image()

    def on_entry_complete(self, entry, slider, max_value):
        self.update_slider_from_entry(entry, slider, max_value)
        self.format_entry(entry)

    def format_entry(self, entry):
        try:
            value = float(entry.get())
            entry.delete(0, tk.END)
            entry.insert(0, f"{value:.2f}")
        except ValueError:
            entry.delete(0, tk.END)
            entry.insert(0, "0.00")

    def save_right_click_values_with_prompt(self):
        response = messagebox.askyesnocancel("Save Registry", "Would you like to save the current registry before saving any edits?")
        if response is None:
            return
        elif response:
            self.controller.show_frame("BackupView")
        self.save_right_click_values()

    def save_right_click_values(self):
        right_click_values = {
            'RightClickZoneWidth': int(float(self.entry_width.get()) * 1000),
            'RightClickZoneHeight': int(float(self.entry_height.get()) * 1000),
        }
        self.set_right_click_values(right_click_values)
        print("Right-click zone values saved:", right_click_values)
        prompt_reboot()
