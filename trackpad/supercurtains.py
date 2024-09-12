import customtkinter as ctk
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import tkinter as tk
from tkinter import messagebox
from reboot_prompt import prompt_reboot


class SuperCurtainsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 스크롤 가능한 프레임을 생성
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=500, height=600)
        self.scrollable_frame.pack(fill="both", expand=True)

        # 레지스트리 경로 및 이미지 경로 설정 (Super Curtains용)
        self.registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        self.curtain_keys = ['SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight']
        self.trackpad_img_path = os.path.join("trackpad", "gb4p16_trackpad.jpg")

        # 트랙패드 크기 설정
        self.trackpad_width_cm = 15
        self.trackpad_height_cm = 10.7
        self.trackpad_width_px = 320
        self.trackpad_height_px = 235
        self.trackpad_x = 145
        self.trackpad_y = 245
        self.max_left_right_cm = 7.5
        self.max_top_cm = 5

        # cm를 px로 변환
        self.cm_to_px_width = self.trackpad_width_px / self.trackpad_width_cm
        self.cm_to_px_height = self.trackpad_height_px / self.trackpad_height_cm

        self.setup_ui()

    def setup_ui(self):
        # 트랙패드 이미지 설정
        self.setup_image()

        # 슬라이더 및 입력창 생성
        self.create_slider_input()

        # 저장 버튼
        frame_buttons = ctk.CTkFrame(self.scrollable_frame)
        frame_buttons.pack(pady=10)

        btn_save = ctk.CTkButton(frame_buttons, text="Save", command=self.save_curtain_values_with_prompt)
        btn_save.grid(row=0, column=0, padx=10)

    def setup_image(self):
        # 트랙패드 이미지 표시 설정
        fig, self.ax = plt.subplots(figsize=(6, 4))
        self.img = plt.imread(self.trackpad_img_path)
        self.ax.imshow(self.img)
        self.ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0, wspace=0)

        self.canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.canvas.get_tk_widget().pack(pady=10)

    def create_slider_input(self):
        self.create_slider("Super Curtain Top (Height, cm)", self.max_top_cm, "entry_top", "slider_top")
        self.create_slider("Super Curtain Left (Width, cm)", self.max_left_right_cm, "entry_left", "slider_left")
        self.create_slider("Super Curtain Right (Width, cm)", self.max_left_right_cm, "entry_right", "slider_right")

        self.initialize_slider_values()

    def create_slider(self, label_text, max_value, entry_name, slider_name):
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
        curtain_values = self.get_current_curtains_values()
        self.slider_top.set(curtain_values.get('SuperCurtainTop', 0) / 1000)
        self.slider_left.set(curtain_values.get('SuperCurtainLeft', 0) / 1000)
        self.slider_right.set(curtain_values.get('SuperCurtainRight', 0) / 1000)

        self.update_entry_from_slider(self.slider_top, self.entry_top)
        self.update_entry_from_slider(self.slider_left, self.entry_left)
        self.update_entry_from_slider(self.slider_right, self.entry_right)

        self.update_image()

    def get_current_curtains_values(self):
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

    def set_curtains_values(self, curtain_values):
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
        self.ax.axis('off')

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
        entry.delete(0, "end")
        entry.insert(0, f"{value:.2f}")
        self.update_image()

    def on_entry_complete(self, entry, slider, max_value):
        self.update_slider_from_entry(entry, slider, max_value)
        self.format_entry(entry)

    def format_entry(self, entry):
        try:
            value = float(entry.get())
            entry.delete(0, "end")
            entry.insert(0, f"{value:.2f}")
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, "0.00")

    def save_curtain_values(self):
        curtain_values = {
            'SuperCurtainTop': int(float(self.entry_top.get()) * 1000),
            'SuperCurtainLeft': int(float(self.entry_left.get()) * 1000),
            'SuperCurtainRight': int(float(self.entry_right.get()) * 1000),
        }
        self.set_curtains_values(curtain_values)
        prompt_reboot()

    def back_to_main_menu(self):
        self.controller.show_frame("MainMenu")
        self.reset_visual_elements()

    def reset_visual_elements(self):
        """레지스트리 값에 따라 비주얼 요소들을 초기화"""
        curtain_values = self.get_current_curtains_values()

        self.slider_top.set(curtain_values.get('SuperCurtainTop', 0) / 1000)
        self.entry_top.delete(0, "end")
        self.entry_top.insert(0, str(curtain_values.get('SuperCurtainTop', 0) / 1000))

        self.slider_left.set(curtain_values.get('SuperCurtainLeft', 0) / 1000)
        self.entry_left.delete(0, "end")
        self.entry_left.insert(0, str(curtain_values.get('SuperCurtainLeft', 0) / 1000))
        
        self.slider_right.set(curtain_values.get('SuperCurtainRight', 0) / 1000)
        self.entry_right.delete(0, "end")
        self.entry_right.insert(0, str(curtain_values.get('SuperCurtainRight', 0) / 1000))
        
        self.update_image()
        
    def save_curtain_values_with_prompt(self):
        # Prompt user to ask if they want to backup current registry values
        response = tk.messagebox.askyesnocancel(
            "Save Registry", 
            "Would you like to save the current registry before saving any edits?"
        )
        
        if response is None:  # Cancel
            return
        elif response:  # Yes, backup current values
            #Display backup view
            return
        
        # Continue to save new registry values
        self.save_curtain_values()
