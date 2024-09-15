import customtkinter as ctk
import winreg
import tkinter as tk
from tkinter import messagebox
from reboot_prompt import prompt_reboot

class TaskbarView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 스크롤 가능한 프레임을 생성
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=500, height=600)
        self.scrollable_frame.pack(fill="both", expand=True)

        # 레지스트리 경로 설정 (사용자가 직접 입력)
        self.registry_path = "HKEY_YOUR_TASKBAR_PATH"
        self.taskbar_keys = ['TaskbarWidth', 'TaskbarHeight']

        # 최대 값 설정 (수정 가능)
        self.max_width_cm = 10.0
        self.max_height_cm = 2.0

        # 슬라이더 및 입력창 UI 생성
        self.create_slider_input()

        # 저장 버튼
        frame_buttons = ctk.CTkFrame(self.scrollable_frame)
        frame_buttons.pack(pady=10)

        btn_save = ctk.CTkButton(frame_buttons, text="Save", command=self.save_taskbar_values_with_prompt)
        btn_save.grid(row=0, column=0, padx=10)

    def create_slider_input(self):
        self.create_slider("Taskbar Width (cm)", self.max_width_cm, "entry_width", "slider_width")
        self.create_slider("Taskbar Height (cm)", self.max_height_cm, "entry_height", "slider_height")

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
        taskbar_values = self.get_current_taskbar_values()
        self.slider_width.set(taskbar_values.get('TaskbarWidth', 0) / 1000)
        self.slider_height.set(taskbar_values.get('TaskbarHeight', 0) / 1000)

        self.update_entry_from_slider(self.slider_width, self.entry_width)
        self.update_entry_from_slider(self.slider_height, self.entry_height)

    def get_current_taskbar_values(self):
        taskbar_values = {}
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path, 0, winreg.KEY_READ)
            for key in self.taskbar_keys:
                try:
                    value, _ = winreg.QueryValueEx(reg_key, key)
                    taskbar_values[key] = value
                except FileNotFoundError:
                    taskbar_values[key] = 0
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error reading registry values: {e}")
        return taskbar_values

    def set_taskbar_values(self, taskbar_values):
        try:
            reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.registry_path)
            for key, value in taskbar_values.items():
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
            winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error setting registry values: {e}")

    def update_slider_from_entry(self, entry, slider, max_value):
        try:
            value = float(entry.get())
            if value > max_value:
                value = max_value
            slider.set(value)
        except ValueError:
            pass

    def update_entry_from_slider(self, slider, entry):
        value = slider.get()
        entry.delete(0, "end")
        entry.insert(0, f"{value:.2f}")

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

    def save_taskbar_values(self):
        taskbar_values = {
            'TaskbarWidth': int(float(self.entry_width.get()) * 1000),
            'TaskbarHeight': int(float(self.entry_height.get()) * 1000),
        }
        self.set_taskbar_values(taskbar_values)
        prompt_reboot()

    def save_taskbar_values_with_prompt(self):
        # 사용자에게 레지스트리 값을 저장할 것인지 물음
        response = tk.messagebox.askyesno(
            "Save Registry", 
            "Are you sure you want to save the new registry values?\n\n"
        )
        
        if response is None:  # 취소
            return
        elif response:  # 저장
            self.save_taskbar_values()
