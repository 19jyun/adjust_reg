import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import pywinstyles

class AnimatedSwitch(ctk.CTkFrame):
    def __init__(self, parent, width=80, height=30, bg_color="gray", fg_color="lime", handle_color="white", command=None):
        super().__init__(parent, fg_color=bg_color)
        
        parent_bg_color = self.get_parent_bg_color(parent)
        
        self.width = width
        self.height = height
        self.bg_color = bg_color  # Color when off
        self.fg_color = fg_color  # Color when on
        self.parent_bg_color = parent_bg_color
        self.handle_color = handle_color
        self.command = command  # Function to call when toggled

        # Create the images for both states (on and off)
        self.create_pill_background(self.bg_color)  # Initial state is off
        self.create_handle_image()

        # Create a transparent canvas to hold the custom switch
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, bg=self.parent_bg_color)
        self.canvas.pack()

        # Create a transparent background image for the canvas
        self.create_transparent_background()
        # Use the created transparent image as background for the canvas
        self.bg_image = ImageTk.PhotoImage(self.transparent_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Draw the pill-shaped switch on top of the transparent background
        self.switch_bg = ImageTk.PhotoImage(self.pill_image)
        self.pill_item = self.canvas.create_image(0, 0, anchor="nw", image=self.switch_bg)

        # Draw the handle on top of the pill switch using the antialiased circle image
        self.handle_image = ImageTk.PhotoImage(self.handle_image_resized)

        # Calculate the correct initial left position (same as in animate_switch)
        border_width = 3  # Match the border width of the pill
        left_pos = border_width  # Initial position for the handle in 'off' state

        # Set the initial position of the handle to be the same as the 'off' position
        self.handle = self.canvas.create_image(left_pos, (self.height - self.handle_image_resized.height) // 2, anchor="nw", image=self.handle_image)

        # State tracking
        self.on = False
        self.switch_active = False  # To avoid multiple toggles during animation

        # Bind click event to toggle the switch
        self.canvas.bind("<Button-1>", self.toggle)

    def get_parent_bg_color(self, parent):
        """Get the background color of the parent widget."""
        # Get the parent's background color in RGB format
        try:
            bg = parent.cget("bg")  # Get parent background color
        except:
            bg = "#FFFFFF"  # Default to white if not available

        return bg

    def create_pill_background(self, color):
        """Create a rounded pill-shaped image with a transparent background for the switch."""
        # Create a large image for antialiasing (4x size)
        scale_factor = 4
        large_width, large_height = self.width * scale_factor, self.height * scale_factor
        large_pill_image = Image.new("RGBA", (large_width, large_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(large_pill_image)
        
        # Calculate the large radius for the rounded corners
        large_radius = self.height // 2 * scale_factor

        # Draw a rounded rectangle (pill shape) on the large canvas with a thick outline
        draw.rounded_rectangle(
            [0, 0, large_width, large_height],
            radius=large_radius,
            fill=color,
            outline="black",
            width=scale_factor * 3  # Make the outline thicker for the large image
        )

        # Resize the image to the original size using antialiasing
        self.pill_image = large_pill_image.resize((self.width, self.height), Image.LANCZOS)

    def create_handle_image(self):
        """Create a smooth, antialiased circle image for the handle."""
        scale_factor = 4
        large_handle_size = self.height * scale_factor
        large_handle_image = Image.new("RGBA", (large_handle_size, large_handle_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(large_handle_image)

        # Draw a circle on the larger image with a black outline
        draw.ellipse(
            [scale_factor, scale_factor, large_handle_size - scale_factor, large_handle_size - scale_factor],
            fill=self.handle_color,
            outline="black",
            width=scale_factor * 3  # Use a thicker outline for the larger circle
        )

        # Resize the large handle image to the original size using antialiasing
        self.handle_image_resized = large_handle_image.resize((self.height, self.height), Image.LANCZOS)

    def create_transparent_background(self):
        """Create a fully transparent image to use as the canvas background."""
        self.transparent_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

    def toggle(self, event=None):
        """Toggle the switch animation on click and update the background color."""
        if not self.switch_active:
            self.on = not self.on
            self.switch_active = True

            # Change the pill color based on the toggle state
            new_color = self.fg_color if self.on else self.bg_color
            self.create_pill_background(new_color)

            # Update the canvas item with the new pill image
            self.switch_bg = ImageTk.PhotoImage(self.pill_image)
            self.canvas.itemconfig(self.pill_item, image=self.switch_bg)

            self.animate_switch()
            
            # Execute the command callback if provided
            if self.command:
                self.command()  # Call the function whenever toggled

    def animate_switch(self):
        """Animate the switch handle with ease-out effect."""
        # Calculate y-center to keep the handle vertically centered
        y_center = (self.height - self.handle_image_resized.height) // 2

        # Border width of the pill shape (matches the outline width used when drawing)
        border_width = 3  # This should match the outline width used in create_pill_background()

        # Adjusted left and right positions to remove gaps and align correctly
        left_pos = border_width  # Perfectly align with the left border
        right_pos = self.width - self.height - border_width  # Perfectly align with the right border

        # Use the toggle state to determine start and end positions
        current_pos = self.canvas.coords(self.handle)[0]
        start_pos = current_pos  # Start position is the current handle position
        end_pos = right_pos if self.on else left_pos  # Move to right if toggled on, left if toggled off

        duration = 300  # Total duration of the animation in milliseconds
        steps = 30  # Number of steps in the animation
        step_duration = duration // steps

        def ease_out(t):
            """Ease-out function."""
            return 1 - (1 - t) ** 3

        def move(step):
            nonlocal start_pos
            if step <= steps:
                t = step / steps
                eased_t = ease_out(t)
                current_pos = start_pos + (end_pos - start_pos) * eased_t
                self.canvas.coords(self.handle, current_pos, y_center)  # Keep the handle vertically centered
                self.after(step_duration, move, step + 1)
            else:
                self.switch_active = False

        move(0)


if __name__ == "__main__":
    def on_toggle():
        print("Switch toggled")

    root = tk.Tk()
    root.configure(bg="white")
    switch = AnimatedSwitch(root, command=on_toggle)
    switch.pack(pady=10)
    root.mainloop()
