import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from new_ui_style import NewUIStyle
from reboot_prompt import prompt_reboot
from backup.backup_view import BackupView

class SuperCurtainsView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ui_style = NewUIStyle(NewUIStyle.get_scaling_factor())

        # Registry keys and image paths for Super Curtains
        self.registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        self.curtain_keys = ['SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight']
        self.trackpad_img_path = "trackpad/gb4p16_trackpad.jpg"

        # Trackpad dimensions
        self.trackpad_width_cm = 15
        self.trackpad_height_cm = 10.7
        self.trackpad_width_px = 320
        self.trackpad_height_px = 235
        self.trackpad_x = 145
        self.trackpad_y = 245
        self.max_left_right_cm = 7.5
        self.max_top_cm = 5

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

        btn_save = tk.Button(frame_buttons, text="Save", command=self.save_curtain_values_with_prompt)
        self.ui_style.apply_button_style(btn_save)
        btn_save.grid(row=0, column=0, padx=padding_x)

        btn_back = tk.Button(frame_buttons, text="Back", command=lambda: self.back_to_main_menu())
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
        self.create_slider("Super Curtain Top (Height, cm)", self.max_top_cm, "entry_top", "slider_top", padding_y)
        self.create_slider("Super Curtain Left (Width, cm)", self.max_left_right_cm, "entry_left", "slider_left", padding_y)
        self.create_slider("Super Curtain Right (Width, cm)", self.max_left_right_cm, "entry_right", "slider_right", padding_y)

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
        curtain_values = self.get_current_super_curtains_values()
        self.slider_top.set(curtain_values.get('SuperCurtainTop', 0) / 1000)
        self.slider_left.set(curtain_values.get('SuperCurtainLeft', 0) / 1000)
        self.slider_right.set(curtain_values.get('SuperCurtainRight', 0) / 1000)

    def get_current_super_curtains_values(self):
        curtain_values = {}
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path, 0, winreg.KEY_READ)
            for key in self.curtain_keys:
                try:
                    value, _ = winreg.QueryValueEx(reg_key, key)
                    curtain_values[key] = value
                except FileNotFoundError:
                    curtain_values[key] = 0
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error reading registry values: {e}")
        return curtain_values

    def set_super_curtains_values(self, curtain_values):
        try:
            reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path)
            for key, value in curtain_values.items():
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error setting registry values: {e}")

    def update_image(self):
        self.ax.clear()
        self.ax.imshow(self.img)

        curtain_top = float(self.entry_top.get() or 0)
        curtain_left = float(self.entry_left.get() or 0)
        curtain_right = float(self.entry_right.get() or 0)

        curtain_top_px = curtain_top * self.cm_to_px_height
        curtain_left_px = curtain_left * self.cm_to_px_width
        curtain_right_px = curtain_right * self.cm_to_px_width

        rect_non_curtain = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, self.trackpad_height_px,
                                         linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
        self.ax.add_patch(rect_non_curtain)

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

    def save_curtain_values_with_prompt(self):
        response = messagebox.askyesnocancel("Save Registry", "Would you like to save the current registry before saving any edits?")
        if response is None:
            return
        elif response:
            self.controller.show_frame("BackupView")
        self.save_curtain_values()

    def save_curtain_values(self):
        curtain_values = {
            'SuperCurtainTop': int(float(self.entry_top.get()) * 1000),
            'SuperCurtainLeft': int(float(self.entry_left.get()) * 1000),
            'SuperCurtainRight': int(float(self.entry_right.get()) * 1000),
        }
        self.set_super_curtains_values(curtain_values)
        prompt_reboot()
        
    def reset_visual_elements(self):
        """레지스트리 값에 따라 비주얼 요소들을 원래대로 초기화"""
        # 저장된 레지스트리 값을 다시 로드
        curtain_values = self.get_current_super_curtains_values()

        # 슬라이더와 입력 필드를 저장된 레지스트리 값으로 설정
        self.slider_top.set(curtain_values.get('SuperCurtainTop', 0) / 1000)
        self.entry_top.delete(0, tk.END)
        self.entry_top.insert(0, str(curtain_values.get('SuperCurtainTop', 0) / 1000))

        self.slider_left.set(curtain_values.get('SuperCurtainLeft', 0) / 1000)
        self.entry_left.delete(0, tk.END)
        self.entry_left.insert(0, str(curtain_values.get('SuperCurtainLeft', 0) / 1000))

        self.slider_right.set(curtain_values.get('SuperCurtainRight', 0) / 1000)
        self.entry_right.delete(0, tk.END)
        self.entry_right.insert(0, str(curtain_values.get('SuperCurtainRight', 0) / 1000))

        # 이미지 업데이트 (초록/노란색 영역도 함께 업데이트)
        self.update_image()
        
    def back_to_main_menu(self):
        self.controller.show_frame("MainMenu")
        self.reset_visual_elements() # 저장을 하지 않았으니, visual elements들을 원래대로 되돌린다
