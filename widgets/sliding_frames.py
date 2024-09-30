import customtkinter as ctk
from configuration_manager import ScreenInfo

class SlidingFrame(ctk.CTkFrame):
    def __init__(self, parent, width=None, height=None, x=None, y=None, slide_out_x=None, slide_out_y=None, **kwargs):
        # Set dynamic width/height flags based on provided dimensions
        self.dynamic_width = width is None
        self.dynamic_height = height is None

        # Set initial dimensions to zero if dynamic to prevent premature resizing issues
        initial_width = width if width is not None else 0
        initial_height = height if height is not None else 0

        self.screen_info = ScreenInfo()

        super().__init__(parent, width=initial_width, height=initial_height, **kwargs)

        self.parent = parent
        self.is_visible = False  # Track whether the frame is currently displayed
        self.animation_running = False  # Track whether an animation is currently running

        # Optional placement parameters for sliding in/out
        self.default_x = x
        self.default_y = y
        self.slide_out_x = slide_out_x
        self.slide_out_y = slide_out_y

        # After initial setup, dynamically update dimensions if necessary
        self.after(100, self.update_dimensions)

    def update_dimensions(self):
        """Update the dimensions of the frame based on parent's size, if dynamic."""
        self.parent.update_idletasks()

        if self.dynamic_width:
            self.width = self.parent.winfo_width()
            self.configure(width=self.width)
        else:
            self.width = self.cget("width")

        if self.dynamic_height:
            self.height = self.parent.winfo_height()
            self.configure(height=self.height)
        else:
            self.height = self.cget("height")

        self.configure(width=self.width, height=self.height)
        self.update_idletasks()  # Ensure the size is correctly set

    def slide_in(self):
        """Slide the frame in from the right with animation."""
        if not self.is_visible and not self.animation_running:
            self.update_dimensions()
            self.animation_running = True
            # Start off-screen on the right side of the parent
            self.place_for_sliding(x_offset=int(self.parent.winfo_width() / self.screen_info.dpi)) 
            self._animate_slide(target_x=self._calculate_center_x(), direction="in")

    def slide_out(self, callback=None):
        """Slide the frame out to the right with animation."""
        if self.is_visible and not self.animation_running:
            self.animation_running = True
            slide_out_x = int(self.slide_out_x if self.slide_out_x is not None else self.parent.winfo_width() / self.screen_info.dpi)
            self._animate_slide(target_x=slide_out_x, direction="out", callback=callback)

    def _animate_slide(self, target_x, direction, callback=None):
        """Animate the frame sliding in or out using easing effect."""
        start_x = self.winfo_x()
        distance = target_x - start_x
        steps = 100  # Number of steps for the animation
        delay = 15  # Delay between steps in milliseconds

        def ease_out_cubic(t):
            """Ease-out function for smooth deceleration."""
            return 1 - (1 - t) ** 7

        def slide(step=0):
            if step <= steps:
                t = step / steps  # Normalized time value (0 to 1)
                eased_t = ease_out_cubic(t)  # Apply easing function
                new_x = start_x + distance * eased_t
                self.place(x=new_x, y=self._calculate_center_y())
                self.after(delay, slide, step + 1)
            else:
                self.place(x=target_x, y=self._calculate_center_y())
                if direction == "out":
                    self.place_forget()
                    self.is_visible = False  # Mark frame as hidden
                if direction == "in":
                    self.is_visible = True  # Mark frame as visible
                self.animation_running = False  # Animation completed
                if callback:
                    callback()

        slide()

    # this place automatically centers the frame, despite the DPI
    def _calculate_center_x(self):
        """Calculate the x-coordinate to center the frame."""
        parent_width = self.parent.winfo_width()
        frame_width = self.winfo_width()
        return int((parent_width - frame_width) // 2 / self.screen_info.dpi)

    def _calculate_center_y(self):
        """Calculate the y-coordinate to center the frame vertically."""
        parent_height = self.parent.winfo_height()
        frame_height = self.winfo_height()
        return int((parent_height - frame_height) // 2 / self.screen_info.dpi)

    def place_for_sliding(self, x_offset=0):
        """Custom place method to start off-screen for sliding animation."""
        # Place the frame off-screen on the right side and calculate y-position properly
        self.place(x=x_offset, y=self._calculate_center_y())

    def pack(self, **kwargs):
        """Override pack to use slide_in animation only if not already visible."""
        if not self.is_visible and not self.animation_running:
            self.update_dimensions()
            self.place_for_sliding(x_offset=self.parent.winfo_width())  # Fix the initial placement for sliding
            self.slide_in()

    def pack_forget(self):
        """Override pack_forget to use slide_out animation."""
        if self.is_visible and not self.animation_running:
            self.slide_out()


# Test the SlidingFrame independently
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x300")
    root.update_idletasks()  # Force geometry update to ensure correct size

    sliding_frame = SlidingFrame(root, fg_color="skyblue")
    label = ctk.CTkLabel(sliding_frame, text="Sliding Frame Content", font=("Arial", 24))
    label.pack(expand=True)

    button_on_frame = ctk.CTkButton(sliding_frame, text="Button on Frame")
    label_on_frame = ctk.CTkLabel(sliding_frame, text="Label on Frame")
    button_on_frame.pack()
    label_on_frame.pack()

    show_button = ctk.CTkButton(root, text="Show Frame", command=lambda: sliding_frame.pack())
    show_button.pack(side="left", padx=20, pady=20)

    hide_button = ctk.CTkButton(root, text="Hide Frame", command=lambda: sliding_frame.pack_forget())
    hide_button.pack(side="right", padx=20, pady=20)

    root.mainloop()
