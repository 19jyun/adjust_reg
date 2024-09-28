# button.py
import customtkinter as ctk
import tkinter as tk

class BouncingButton(ctk.CTkButton):
    def __init__(self, parent, text="Bounce!", duration=75, command=None, *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs)
        self.duration = duration  # Total animation duration in milliseconds
        self.steps = 30  # Number of steps for smooth animation
        self.command = command  # Store the command function to execute after bounce

        # Store initial dimensions
        self.original_width = self._current_width
        self.original_height = self._current_height

        # Enlarge parameters for bounce effect
        self.bounce_scale = 1.15  # The button grows by 15% when clicked

        # Bind the click event to trigger the bounce animation
        self.bind("<Button-1>", self.start_bounce)

    def start_bounce(self, event=None):
        """Start the subtle bounce effect animation on click."""
        self.bounce(step=0)

    def bounce(self, step):
        """Animate the button to grow and shrink subtly, simulating a bounce."""
        if step < self.steps:
            # Calculate the scale factor using an ease-out effect
            t = step / self.steps
            scale_factor = 1 + (self.bounce_scale - 1) * self.ease_out(t) if step < self.steps // 2 else \
                           1 + (self.bounce_scale - 1) * self.ease_out(1 - t)
            
            # Apply the scale factor to the button's width and height
            new_width = int(self.original_width * scale_factor)
            new_height = int(self.original_height * scale_factor)

            # Adjust button dimensions
            self.configure(width=new_width, height=new_height)

            # Continue the animation
            self.after(self.duration // self.steps, self.bounce, step + 1)
        else:
            # Restore to the original size after the animation
            self.configure(width=self.original_width, height=self.original_height)

            # Execute the command if provided
            if self.command:
                self.command()

    def ease_out(self, t):
        """Ease-out function for a smooth animation."""
        return 1 - (1 - t) ** 3

# Test the BouncingButton with a simple UI
if __name__ == "__main__":
    # Create a basic CustomTkinter window
    root = ctk.CTk()
    root.geometry("400x300")
    root.title("Bouncing Button Test")

    # Define a test function to be called on click
    def test_command():
        print("Button Clicked!")

    # Create and place the bouncing button in the middle of the window with a command
    bouncing_button = BouncingButton(root, text="Click Me!", fg_color="blue", hover_color="lightblue", width=150, height=40, command=test_command)
    bouncing_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the button in the window

    # Run the application
    root.mainloop()
