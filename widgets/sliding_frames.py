import customtkinter as ctk
import tkinter as tk


class SlidingFrame(ctk.CTkFrame):
    def __init__(self, parent, width=400, height=400, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.parent = parent
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Track whether the frame is currently displayed
        self.is_visible = False

    def slide_in(self):
        """Slide the frame in from the right with acceleration and deceleration."""
        if not self.is_visible:
            self.place(x=self.width, y=0)  # Start off-screen
            self._animate_slide(target_x=0, direction="in")
            self.is_visible = True

    def slide_out(self, callback=None):
        """Slide the frame out to the right with acceleration and deceleration."""
        if self.is_visible:
            self._animate_slide(target_x=self.width, direction="out", callback=callback)
            self.is_visible = False

    def _animate_slide(self, target_x, direction, callback=None):
        """Animate the frame sliding in or out using easing function."""
        start_x = self.winfo_x()
        distance = target_x - start_x
        steps = 100  # Increased steps for smoother animation
        delay = 10  # Decreased delay for faster transition

        # Using an ease-out function to apply acceleration and deceleration
        def ease_out_cubic(t):
            return 1 - (1 - t) ** 8

        def slide(step=0):
            if step <= steps:
                t = step / steps  # Normalized time value
                eased_t = ease_out_cubic(t)  # Apply easing
                new_x = start_x + distance * eased_t
                self.place(x=new_x, y=0)
                self.after(delay, slide, step + 1)
            else:
                # Set the final position
                self.place(x=target_x, y=0)
                if direction == "out":
                    self.place_forget()  # Hide the frame after sliding out
                if callback:
                    callback()  # Call the callback if provided

        slide()

    def pack(self, **kwargs):
        """Override pack to use slide_in animation."""
        if not self.is_visible:
            self.place(x=self.width, y=0)
            self.slide_in()

    def pack_forget(self):
        """Override pack_forget to use slide_out animation."""
        self.slide_out()


# Test the SlidingFrame independently
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x400")

    # Create a SlidingFrame
    sliding_frame = SlidingFrame(root, width=800, height=400, fg_color="skyblue")
    label = ctk.CTkLabel(sliding_frame, text="Sliding Frame Content", font=("Arial", 24))
    label.pack(expand=True)

    button_on_frame = ctk.CTkButton(sliding_frame, text="Button on Frame")
    label_on_frame = ctk.CTkLabel(sliding_frame, text="Label on Frame")
    button_on_frame.pack()
    label_on_frame.pack()

    # Button to show the sliding frame
    show_button = ctk.CTkButton(root, text="Show Frame", command=lambda: sliding_frame.pack())
    show_button.pack(side="left", padx=20, pady=20)

    # Button to hide the sliding frame
    hide_button = ctk.CTkButton(root, text="Hide Frame", command=lambda: sliding_frame.pack_forget())
    hide_button.pack(side="right", padx=20, pady=20)

    root.mainloop()
