import customtkinter as ctk
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class RightClickView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 스크롤 가능한 프레임을 생성
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=500, height=600)
        self.scrollable_frame.pack(fill="both", expand=True)

        # 레지스트리 경로 및 이미지 경로 설정
        self.registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        self.right_click_keys = ['RightClickZoneWidth', 'RightClickZoneHeight']
        self.trackpad_img_path = os.path.join("trackpad", "gb4p16_trackpad.jpg")

        # 트랙패드 크기 설정
        self.trackpad_width_cm = 15
        self.trackpad_height_cm = 10.7
        self.trackpad_width_px = 320
        self.trackpad_height_px = 235
        self.trackpad_x = 145
        self.trackpad_y = 245
        self.max_width_cm = 7.5
        self.max_height_cm = 5

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

        btn_save = ctk.CTkButton(frame_buttons, text="Save", command=self.save_right_click_values)
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
        self.create_slider("Right-Click Zone Width (cm)", self.max_width_cm, "entry_width", "slider_width")
        self.create_slider("Right-Click Zone Height (cm)", self.max_height_cm, "entry_height", "slider_height")

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
        right_click_values = self.get_current_right_click_values()
        self.slider_width.set(right_click_values.get('RightClickZoneWidth', 0) / 1000)
        self.slider_height.set(right_click_values.get('RightClickZoneHeight', 0) / 1000)

        self.update_image()

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
        self.ax.axis('off')

        # 슬라이더에서 가져온 값 (cm)
        right_click_width = float(self.entry_width.get() or 0)
        right_click_height = float(self.entry_height.get() or 0)

        # cm를 픽셀로 변환
        right_click_width_px = right_click_width * self.cm_to_px_width
        right_click_height_px = right_click_height * self.cm_to_px_height

        # 전체 트랙패드 이미지에 대한 사각형 (노란색, 비클릭 영역)
        rect_non_click = plt.Rectangle((self.trackpad_x, self.trackpad_y), self.trackpad_width_px, self.trackpad_height_px,
                                       linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
        self.ax.add_patch(rect_non_click)

        # 오른쪽 하단에서 시작해서 클릭 영역을 확장 (초록색, 클릭 영역)
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

    def save_right_click_values(self):
        right_click_values = {
            'RightClickZoneWidth': int(float(self.entry_width.get()) * 1000),
            'RightClickZoneHeight': int(float(self.entry_height.get()) * 1000),
        }
        self.set_right_click_values(right_click_values)

    def back_to_main_menu(self):
        self.controller.show_frame("MainMenu")
        self.reset_visual_elements()

    def reset_visual_elements(self):
        """레지스트리 값에 따라 비주얼 요소들을 초기화"""
        right_click_values = self.get_current_right_click_values()

        self.slider_width.set(right_click_values.get('RightClickZoneWidth', 0) / 1000)
        self.entry_width.delete(0, "end")
        self.entry_width.insert(0, str(right_click_values.get('RightClickZoneWidth', 0) / 1000))

        self.slider_height.set(right_click_values.get('RightClickZoneHeight', 0) / 1000)
        self.entry_height.delete(0, "end")
        self.entry_height.insert(0, str(right_click_values.get('RightClickZoneHeight', 0) / 1000))

        # 이미지 업데이트 (초록/노란색 영역도 함께 업데이트)
        self.update_image()
