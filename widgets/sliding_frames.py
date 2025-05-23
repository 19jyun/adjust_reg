import customtkinter as ctk
from configuration_manager import ScreenInfo

class SlidingFrame(ctk.CTkFrame):
    # Class-level attribute to track global animation state across all instances
    animation_lock = False

    def __init__(self, parent, width=None, height=None, x=None, y=None, slide_out_x=None, slide_out_y=None, **kwargs):
        """Initialize the SlidingFrame with fixed dimensions."""
        self.screen_info = ScreenInfo()
        self.width = width if width is not None else self.screen_info.window_width
        self.height = height if height is not None else self.screen_info.window_height

        super().__init__(parent, **kwargs)
        self.configure(width=self.width, height=self.height)

        self.parent = parent
        self.is_visible = False  # Track whether the frame is currently displayed
        self.animation_running = False  # Track whether an animation is currently running

        # Optional placement parameters for sliding in/out
        self.default_x = x
        self.default_y = y
        self.slide_out_x = slide_out_x
        self.slide_out_y = slide_out_y

    def slide_in(self):
        """Slide the frame in from the right with animation."""
        if not self.is_visible and not self.animation_running and not SlidingFrame.animation_lock:
            self.animation_running = True
            SlidingFrame.animation_lock = True  # Acquire the global animation lock
            self.place_for_sliding(x_offset=-self.parent.winfo_width()) 
            self._animate_slide(target_x=self._calculate_center_x(), direction="in")

    def slide_out(self, callback=None):
        """Slide the frame out to the right with animation."""
        if self.is_visible and not self.animation_running and not SlidingFrame.animation_lock:
            self.animation_running = True
            SlidingFrame.animation_lock = True  # Acquire the global animation lock
            slide_out_x = self.slide_out_x if self.slide_out_x is not None else self.parent.winfo_width()
            self._animate_slide(target_x=slide_out_x, direction="out", callback=callback)

    def _animate_slide(self, target_x, direction, callback=None):
        """Animate the frame sliding in or out using easing effect."""
        start_x = self.winfo_x()
        distance = target_x - start_x
        steps = 100  # Number of steps for the animation
        delay = 5  # Delay between steps in milliseconds

        def ease_out_cubic(t):
            """Ease-out function for smooth deceleration."""
            return 1 - (1 - t) ** 6

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
                SlidingFrame.animation_lock = False  # Release the global animation lock
                if callback:
                    callback()

        slide()

    # Calculate x and y to center the frame despite DPI scaling
    def _calculate_center_x(self):
        """Calculate the x-coordinate to center the frame."""
        parent_width = self.parent.winfo_width()
        frame_width = self.winfo_width()
        return int(((parent_width - frame_width) // 2) / self.screen_info.dpi)

    def _calculate_center_y(self):
        """Calculate the y-coordinate to center the frame vertically."""
        parent_height = self.parent.winfo_height()
        frame_height = self.winfo_height()
        return int(((parent_height - frame_height) // 2) / self.screen_info.dpi)

    def place_for_sliding(self, x_offset=0):
        """Custom place method to start off-screen for sliding animation."""
        # Place the frame off-screen on the right side and calculate y-position properly
        self.update_idletasks()
        self.place(x=x_offset, y=self._calculate_center_y())

    def display(self, x=None, y=None):
        """Display the frame in the initial position for the sliding-out animation."""
        self.update_idletasks()  # Ensure widget dimensions are properly calculated

        pos_x = x if x is not None else 0
        pos_y = y if y is not None else 0

        self.place(x=pos_x, y=pos_y)  # Place the frame at the initial position
        self.is_visible = True  # Mark frame as visible


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
