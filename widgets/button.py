import customtkinter as ctk
import tkinter as tk

class BouncingButton(ctk.CTkButton):
    def __init__(self, parent, text="Bounce!", duration=75, command=None, *args, **kwargs):
        # Store initial colors passed during initialization
        self.initial_fg_color = kwargs.get("fg_color", "blue")
        self.initial_hover_color = kwargs.get("hover_color", "lightblue")

        super().__init__(parent, text=text, *args, **kwargs)

        self.duration = duration  # Total animation duration in milliseconds
        self.steps = 30  # Number of steps for smooth animation
        self.command = command  # Store the command function to execute after bounce

        # Store initial dimensions
        self.original_width = self._current_width
        self.original_height = self._current_height

        # Enlarge parameters for bounce effect
        self.bounce_scale = 1.1  # The button grows by 15% when clicked

        # Default state is "normal"
        self.state = "normal"

        # Bind the click event to trigger the bounce animation
        self.bind("<Button-1>", self.start_bounce)

    def start_bounce(self, event=None):
        """Start the subtle bounce effect animation on click if button is enabled."""
        # Check if button is enabled before starting the bounce animation
        if self.state == "normal":
            self.bounce(step=0)

    def bounce(self, step):
        """Animate the button to grow and shrink subtly, simulating a bounce."""
        if step < self.steps:
            # Calculate the scale factor using an ease-out effect
            # change the minus sign to plus sign to make the button grow
            t = step / self.steps
            scale_factor = 1 - (self.bounce_scale - 1) * self.ease_out(t) if step < self.steps // 2 else \
                           1 - (self.bounce_scale - 1) * self.ease_out(1 - t)
            
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
            if self.command and self.state == "normal":
                self.command()

    def ease_out(self, t):
        """Ease-out function for a smooth animation."""
        return 1 - (1 - t) ** 6

    def configure(self, **kwargs):
        """Override configure method to handle state changes."""
        if "state" in kwargs:
            self.state = kwargs.pop("state")

            # If state is disabled, change appearance to reflect disabled state
            if self.state == "disabled":
                # Store the current colors before changing them
                self.previous_fg_color = self.cget("fg_color")
                self.previous_hover_color = self.cget("hover_color")

                # Change colors or styles for a "disabled" look
                super().configure(fg_color="grey", hover_color="darkgrey")
                # Unbind the click event so no animation occurs
                self.unbind("<Button-1>")

            else:
                # Restore the button's original appearance and re-bind the click event
                original_fg_color = getattr(self, "previous_fg_color", self.initial_fg_color)
                original_hover_color = getattr(self, "previous_hover_color", self.initial_hover_color)
                
                super().configure(fg_color=original_fg_color, hover_color=original_hover_color)
                self.bind("<Button-1>", self.start_bounce)

        # Apply any other configurations passed to the superclass method
        super().configure(**kwargs)
