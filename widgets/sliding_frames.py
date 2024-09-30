import customtkinter as ctk
from configuration_manager import ScreenInfo

class SlidingFrame(ctk.CTkFrame):
    def __init__(self, parent, width=None, height=None, x=None, y=None, slide_out_x=None, slide_out_y=None, **kwargs):
        """Initialize the SlidingFrame with fixed dimensions."""
        # Set initial dimensions, or default to zero if not provided
        self.width = width if width is not None else parent.winfo_width()
        self.height = height if height is not None else parent.winfo_height()

        self.screen_info = ScreenInfo()

        # Initialize the frame with the provided dimensions
        super().__init__(parent, width=self.width, height=self.height, **kwargs)

        self.parent = parent
        self.is_visible = False  # Track whether the frame is currently displayed
        self.animation_running = False  # Track whether an animation is currently running

        # Optional placement parameters for sliding in/out
        self.default_x = x
        self.default_y = y
        self.slide_out_x = slide_out_x
        self.slide_out_y = slide_out_y
        
        self.update_idletasks()
        self.width = self.winfo_width()
        self.height = self.winfo_height()

    def slide_in(self):
        """Slide the frame in from the right with animation."""
        if not self.is_visible and not self.animation_running:
            self.animation_running = True
            # Start off-screen on the right side of the parent
            self.place_for_sliding(x_offset=-self.parent.winfo_width()) 
            self._animate_slide(target_x=self._calculate_center_x(), direction="in")

    def slide_out(self, callback=None):
        """Slide the frame out to the right with animation."""
        if self.is_visible and not self.animation_running:
            self.animation_running = True
            slide_out_x = self.slide_out_x if self.slide_out_x is not None else self.parent.winfo_width()
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
        return (parent_width - frame_width) // 2

    def _calculate_center_y(self):
        """Calculate the y-coordinate to center the frame vertically."""
        parent_height = self.parent.winfo_height()
        frame_height = self.winfo_height()
        return (parent_height - frame_height) // 2

    def place_for_sliding(self, x_offset=0):
        """Custom place method to start off-screen for sliding animation."""
        # Place the frame off-screen on the right side and calculate y-position properly
        self.update_idletasks()
        self.place(x=x_offset, y=self._calculate_center_y())

    def pack(self, **kwargs):
        """Override pack to use slide_in animation."""
        if not self.is_visible and not self.animation_running:
            # Update widget dimensions and initial placement for sliding
            self.update_idletasks()  # Ensure correct dimensions before sliding
            self.place_for_sliding(x_offset=self.parent.winfo_width())
            self.slide_in()
        self.tkraise()

    def pack_forget(self):
        """Override pack_forget to use slide_out animation."""
        if self.is_visible and not self.animation_running:
            self.slide_out()
