import tkinter as tk
from new_ui_style import NewUIStyle
from curtains_view import CurtainsView
from supercurtains_view import SuperCurtainsView
from rightclick_view import RightClickView
from settings_view import SettingsView
from backup_view import BackupView

class MainApplication(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Trackpad Registry Manager")
        self.scale_factor = NewUIStyle.get_scaling_factor()
        self.ui_style = NewUIStyle(self.scale_factor)
        self.geometry(self.ui_style.get_window_geometry())
        self.overrideredirect(True)
        self.frames = {}

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.create_frames(container)

    def create_frames(self, container):
        for F in (MainMenu, CurtainsView, SuperCurtainsView, RightClickView, BackupView, SettingsView):
            page_name = F.__name__
            frame = self.ui_style.create_scrollable_frame(container)
            if F == BackupView:
                page_frame = F(parent=frame.scrollable_frame, controller=self, 
                               set_curtains_values=self.set_curtains_values,
                               set_super_curtains_values=self.set_super_curtains_values,
                               set_right_click_values=self.set_right_click_values,
                               get_current_curtains_values=self.get_current_curtains_values,
                               get_current_super_curtains_values=self.get_current_super_curtains_values,
                               get_current_right_click_values=self.get_current_right_click_values)
            else:
                page_frame = F(parent=frame.scrollable_frame, controller=self)
            self.frames[page_name] = frame
            page_frame.pack(fill="both", expand=True)
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # 필요한 메서드들을 정의합니다.
    def set_curtains_values(self, values):
        print("Setting curtains values:", values)

    def set_super_curtains_values(self, values):
        print("Setting super curtains values:", values)

    def set_right_click_values(self, values):
        print("Setting right-click values:", values)

    def get_current_curtains_values(self):
        print("Getting current curtains values")
        return {}

    def get_current_super_curtains_values(self):
        print("Getting current super curtains values")
        return {}

    def get_current_right_click_values(self):
        print("Getting current right-click values")
        return {}

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ui_style = controller.ui_style

        btn_curtains = tk.Button(self, text="Set Curtains", command=lambda: controller.show_frame("CurtainsView"))
        self.ui_style.apply_button_style(btn_curtains)
        btn_curtains.pack(pady=10)

        btn_super_curtains = tk.Button(self, text="Set Super Curtains", command=lambda: controller.show_frame("SuperCurtainsView"))
        self.ui_style.apply_button_style(btn_super_curtains)
        btn_super_curtains.pack(pady=10)

        btn_right_click_zone = tk.Button(self, text="Set Right-click Zone", command=lambda: controller.show_frame("RightClickView"))
        self.ui_style.apply_button_style(btn_right_click_zone)
        btn_right_click_zone.pack(pady=10)

        btn_backup_manager = tk.Button(self, text="Backup Manager", command=lambda: controller.show_frame("BackupView"))
        self.ui_style.apply_button_style(btn_backup_manager)
        btn_backup_manager.pack(pady=10)

        btn_settings = tk.Button(self, text="Settings", command=lambda: controller.show_frame("SettingsView"))
        self.ui_style.apply_button_style(btn_settings)
        btn_settings.pack(pady=10)

        btn_quit = tk.Button(self, text="Quit", command=self.controller.quit)
        self.ui_style.apply_button_style(btn_quit)
        btn_quit.pack(pady=10)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()