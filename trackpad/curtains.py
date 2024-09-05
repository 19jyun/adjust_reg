import tkinter as tk
from tkinter import ttk
import winreg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 레지스트리 경로 및 키
registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
curtain_keys = ['CurtainTop', 'CurtainLeft', 'CurtainRight', 'CurtainBottom']

# 트랙패드 위치 및 크기 설정 (이미지에서 트랙패드 영역)
TRACKPAD_X = 145   # 트랙패드의 x 좌표 (이미지의 픽셀 단위로)
TRACKPAD_Y = 245   # 트랙패드의 y 좌표 (이미지의 픽셀 단위로)
TRACKPAD_WIDTH = 320  # 트랙패드의 너비
TRACKPAD_HEIGHT = 235  # 트랙패드의 높이

# 현재 커튼 레지스트리 값을 읽는 함수
def get_current_curtains_values():
    curtain_values = {}
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        for key in curtain_keys:
            try:
                value, reg_type = winreg.QueryValueEx(reg_key, key)
                curtain_values[key] = value
            except FileNotFoundError:
                curtain_values[key] = 0  # 기본값이 없는 경우 0으로 처리
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error reading registry values: {e}")
    return curtain_values

# 레지스트리 값을 설정하는 함수
def set_curtains_values(curtain_values):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        for key, value in curtain_values.items():
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error setting registry values: {e}")

# 이미지를 업데이트하는 함수
def update_image():
    ax.clear()

    # 원본 이미지를 그려줍니다
    ax.imshow(img)

    # 커튼 구역을 설정 (트랙패드 영역에서만)
    curtain_top = slider_top.get()
    curtain_left = slider_left.get()
    curtain_right = slider_right.get()

    # 트랙패드의 노란색 non-curtain 영역 그리기 (노란색으로 기본 배경)
    rect_non_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH, TRACKPAD_HEIGHT, 
                                     linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
    ax.add_patch(rect_non_curtain)

    # # 커튼 영역 그리기 (초록색으로 커튼 영역을 확장)
    # left_x = TRACKPAD_X + curtain_left  # 왼쪽 커튼 시작 지점
    # right_x = TRACKPAD_X + TRACKPAD_WIDTH - curtain_right  # 오른쪽 커튼 시작 지점
    # top_y = TRACKPAD_Y - curtain_top  # 상단 커튼 지점

    left_curtain_x = TRACKPAD_X  # 왼쪽 커튼 끝 지점
    left_curtain_y = TRACKPAD_Y  # 왼쪽 커튼 끝 지점
    left_curtain_width = curtain_left
    left_curtain_height = TRACKPAD_HEIGHT
    
    right_curtain_x = TRACKPAD_X + TRACKPAD_WIDTH  # 오른쪽 커튼 시작 지점
    right_curtain_y = TRACKPAD_Y  # 오른쪽 커튼 시작 지점
    right_curtain_width = -curtain_right
    right_curtain_height = TRACKPAD_HEIGHT
    
    top_curtain_x = TRACKPAD_X  # 상단 커튼 시작 지점
    top_curtain_y = TRACKPAD_Y  # 상단 커튼 시작 지점
    top_curtain_width = TRACKPAD_WIDTH
    top_curtain_height = curtain_top

    # 커튼이 적용된 사각형을 초록색으로 그리기
    left_curtain = plt.Rectangle((left_curtain_x, left_curtain_y), left_curtain_width, left_curtain_height,
                                    linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    right_curtain = plt.Rectangle((right_curtain_x, right_curtain_y), right_curtain_width, right_curtain_height,
                                    linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    top_curtain = plt.Rectangle((top_curtain_x, top_curtain_y), top_curtain_width, top_curtain_height,
                                    linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    
    ax.add_patch(left_curtain)
    ax.add_patch(right_curtain)
    ax.add_patch(top_curtain)

    # 좌표축 제거
    plt.gca().axes.xaxis.set_visible(False)
    plt.gca().axes.yaxis.set_visible(False)
    
    # 이미지 업데이트
    canvas.draw()

    # 슬라이더 옆의 숫자 업데이트
    label_top_value.config(text=f"{int(slider_top.get())}")
    label_left_value.config(text=f"{int(slider_left.get())}")
    label_right_value.config(text=f"{int(slider_right.get())}")

# 커튼 설정 GUI 창을 생성하는 함수
def create_curtains_window():
    sub_window = tk.Toplevel()
    sub_window.title("Curtains Settings")

    # 이미지 표시할 matplotlib 설정
    global ax, canvas, img
    fig, ax = plt.subplots(figsize=(6, 4))

    img = plt.imread("trackpad/gb4p16_trackpad.jpg")  # 사용자 이미지 파일 로드
    ax.imshow(img)

    canvas = FigureCanvasTkAgg(fig, master=sub_window)
    canvas.get_tk_widget().pack()

    # 슬라이더 설정 및 숫자 표시
    global slider_top, slider_left, slider_right, label_top_value, label_left_value, label_right_value

    label_top = tk.Label(sub_window, text="Curtain Top (Height)")
    label_top.pack(pady=5)
    slider_top = ttk.Scale(sub_window, from_=0, to=TRACKPAD_HEIGHT, orient='horizontal', command=lambda x: update_image())
    slider_top.pack(pady=5)
    label_top_value = tk.Label(sub_window, text="0")  # 슬라이더 옆에 숫자 표시
    label_top_value.pack(pady=5)

    label_left = tk.Label(sub_window, text="Curtain Left (Width)")
    label_left.pack(pady=5)
    slider_left = ttk.Scale(sub_window, from_=0, to=TRACKPAD_WIDTH//2, orient='horizontal', command=lambda x: update_image())
    slider_left.pack(pady=5)
    label_left_value = tk.Label(sub_window, text="0")  # 슬라이더 옆에 숫자 표시
    label_left_value.pack(pady=5)

    label_right = tk.Label(sub_window, text="Curtain Right (Width)")
    label_right.pack(pady=5)
    slider_right = ttk.Scale(sub_window, from_=0, to=TRACKPAD_WIDTH//2, orient='horizontal', command=lambda x: update_image())
    slider_right.pack(pady=5)
    label_right_value = tk.Label(sub_window, text="0")  # 슬라이더 옆에 숫자 표시
    label_right_value.pack(pady=5)

    # 초기 슬라이더 값을 현재 레지스트리 값으로 설정
    curtain_values = get_current_curtains_values()
    slider_top.set(curtain_values.get('CurtainTop', 0))
    slider_left.set(curtain_values.get('CurtainLeft', 0))
    slider_right.set(curtain_values.get('CurtainRight', 0))

    # 저장 버튼
    btn_save = tk.Button(sub_window, text="Save Settings", command=lambda: save_curtain_values())
    btn_save.pack(pady=10)

# 커튼 레지스트리 값을 저장하는 함수
def save_curtain_values():
    curtain_values = {
        'CurtainTop': slider_top.get(),
        'CurtainLeft': slider_left.get(),
        'CurtainRight': slider_right.get(),
    }
    set_curtains_values(curtain_values)
    print("Curtain values saved:", curtain_values)
