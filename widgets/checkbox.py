import customtkinter as ctk
import tkinter as tk

class BouncingCheckBox(ctk.CTkCheckBox):
    def __init__(self, parent, text="", width=20, height=20, duration=200, bounce_scale=1.3, *args, **kwargs):
        super().__init__(parent, text=text, width=width, height=height, *args, **kwargs)
        self.duration = duration  # Total animation duration in milliseconds
        self.steps = 15  # Number of steps for smooth animation
        self.bounce_scale = bounce_scale  # Scale factor for the bounce effect

        # Store initial dimensions
        self.original_width = width
        self.original_height = height

        # Bind the click event to trigger the bounce animation
        self.bind("<Button-1>", self.start_bounce)

    def start_bounce(self, event=None):
        """Start the subtle bounce effect animation on click."""
        self.bounce(step=0)

    def bounce(self, step):
        """Animate the checkbox to grow and shrink subtly, simulating a bounce."""
        if step < self.steps:
            # Calculate the scale factor for growing and shrinking
            t = step / self.steps
            scale_factor = 1 + (self.bounce_scale - 1) * self.ease_out(t) if step < self.steps // 2 else \
                           1 - (self.bounce_scale - 1) * self.ease_out(t - 0.5)

            # Apply the scale factor to the checkbox's width and height
            new_width = int(self.original_width * scale_factor)
            new_height = int(self.original_height * scale_factor)

            # Adjust checkbox dimensions
            self.configure(width=new_width, height=new_height)

            # Continue the animation
            self.after(self.duration // self.steps, self.bounce, step + 1)
        else:
            # Restore to the original size after the animation
            self.configure(width=self.original_width, height=self.original_height)

    def ease_out(self, t):
        """Ease-out function for a smooth animation."""
        return 1 - (1 - t) ** 3

# Test the BouncingCheckBox with a simple UI
if __name__ == "__main__":
    # Create a basic CustomTkinter window
    root = ctk.CTk()
    root.geometry("400x300")
    root.title("Bouncing CheckBox Test")

    # Create and place a few bouncing checkboxes with different colors and sizes
    checkbox1 = BouncingCheckBox(root, text="Option 1", width=25, height=25, fg_color="blue", hover_color="lightblue", duration=300, bounce_scale=1.4)
    checkbox1.pack(pady=20)

    checkbox2 = BouncingCheckBox(root, text="Option 2", width=30, height=30, fg_color="green", hover_color="lightgreen", duration=300, bounce_scale=1.4)
    checkbox2.pack(pady=20)

    checkbox3 = BouncingCheckBox(root, text="Option 3", width=35, height=35, fg_color="red", hover_color="lightcoral", duration=300, bounce_scale=1.4)
    checkbox3.pack(pady=20)

    # Run the application
    root.mainloop()
