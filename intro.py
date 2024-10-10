# intro.py
import customtkinter as ctk
import os
from PIL import Image
from configuration_manager import ScreenInfo
from widgets.sliding_frames import SlidingFrame


class IntroView(SlidingFrame):
    def __init__(self, parent, controller=None):
        # Screen information for dynamic scaling and geometry
        self.screen_info = ScreenInfo()
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller

        # Force parent update to get correct dimensions
        self.parent.update_idletasks()

        # Correct the size if it's not applied
        self.configure(width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.pack_propagate(0)
        # Base directory for locating resources (images)
        base_dir = os.path.dirname(__file__)
        # Correct path to the icon image in the `tray_icons` folder
        self.icon_image_path = os.path.join(base_dir, "tray_icons", "registry.png")

        #print("Intro Frame Size:", self.screen_info.window_width, self.screen_info.window_height)
        
        # Create a central frame to hold the image and text
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(pady=20, padx=20, expand=True)

        #self.content_frame.configure(width=self.screen_info.window_width, height=self.screen_info.window_height)
        #self.content_frame.pack_propagate(0)

        # Display the program's logo if the image file exists
        if os.path.exists(self.icon_image_path):
            self.icon_image = ctk.CTkImage(Image.open(self.icon_image_path), size=(120, 120))
            self.icon_label = ctk.CTkLabel(self.content_frame, image=self.icon_image, text="")
            self.icon_label.pack(pady=(30, 15))  # Place image with some padding

        # Display the program name below the logo
        self.program_name_label = ctk.CTkLabel(
            self.content_frame,
            text="MyWindows",
            font=("Arial", 28, "bold"),
        )
        self.program_name_label.pack(pady=10)

        # Automatically slide out and pack_forget after 2 seconds
        self.after(2000, self.hide_intro_frame)

    def hide_intro_frame(self):
        """Slide out the intro frame and hide it."""
        self.pack_forget()  # Slide out and hide the frame after 2 seconds
