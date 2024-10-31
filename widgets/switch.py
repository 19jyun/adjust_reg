import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageColor

class AnimatedSwitch(ctk.CTkFrame):
    def __init__(self, parent, width=80, height=30, fg_color="lime", bg_color= "#808080", handle_color="white", command=None, initial_state=False):
        # Set the frame background to transparent, so it blends with the parent
        super().__init__(parent, fg_color="transparent")

        # Initialize parameters
        self.parent = parent
        self.width = width
        self.height = height
        self.switch_bg_color = self.get_parent_color()
        self.bg_color = bg_color  # Color for the OFF state
        self.fg_color = fg_color  # ON state color
        self.handle_color = handle_color
        self.command = command
        self.on = initial_state  # Set initial ON/OFF state

        # Create the canvas and blend with parent background
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, bg=self.switch_bg_color)
        self.canvas.pack()

        # Create images for both states (ON and OFF)
        self.create_pill_background(self.bg_color if not self.on else self.fg_color)
        self.create_handle_image()

        # Draw pill and handle images
        self.switch_bg = ImageTk.PhotoImage(self.pill_image)
        self.pill_item = self.canvas.create_image(0, 0, anchor="nw", image=self.switch_bg)
        self.handle_image = ImageTk.PhotoImage(self.handle_image_resized)
        self.handle = self.canvas.create_image(
            self.get_knob_position(),  # Use get_knob_position() for initial position
            (self.height - self.handle_image_resized.height) // 2,
            anchor="nw",
            image=self.handle_image
        )

        # Bind click event to toggle the switch
        self.canvas.bind("<Button-1>", self.toggle)

    def create_switch(self):
        """Create the switch with the current state and colors."""
        self.create_pill_background(self.fg_color if self.on else self.bg_color)
        self.switch_bg = ImageTk.PhotoImage(self.pill_image)
        self.pill_item = self.canvas.create_image(0, 0, anchor="nw", image=self.switch_bg)
        self.handle_image = ImageTk.PhotoImage(self.handle_image_resized)
        self.handle = self.canvas.create_image(
            self.get_knob_position(),  # Use get_knob_position() for initial position
            (self.height - self.handle_image_resized.height) // 2,
            anchor="nw",
            image=self.handle_image
        )

    def create_pill_background(self, color=None):
        """Create a rounded pill-shaped image with a transparent background for the switch."""
        
        if color is None:
            color = self.get_parent_color()
        
        scale_factor = 4
        large_width, large_height = self.width * scale_factor, self.height * scale_factor
        large_pill_image = Image.new("RGBA", (large_width, large_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(large_pill_image)
        large_radius = self.height // 2 * scale_factor
        outline_width = 3 * scale_factor

        # Draw the rounded rectangle(Pill) with color fill and a black outline
        draw.rounded_rectangle(
            [outline_width // 2, outline_width // 2, large_width - outline_width // 2, large_height - outline_width // 2],
            radius=large_radius,
            fill=color,
            outline="black",
            width=outline_width
        )

        # Resize to final dimensions
        self.pill_image = large_pill_image.resize((self.width, self.height), Image.LANCZOS)

    def get_parent_color(self):
        
        if ctk.get_appearance_mode() == "system":
            print("System")
            
        
        return "#DBDBDB" if ctk.get_appearance_mode() == "Light" else "#2B2B2B"

    def create_handle_image(self):
        """Create a smooth, antialiased circle image for the handle."""
        scale_factor = 4
        large_handle_size = self.height * scale_factor
        large_handle_image = Image.new("RGBA", (large_handle_size, large_handle_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(large_handle_image)
        draw.ellipse(
            [scale_factor, scale_factor, large_handle_size - scale_factor, large_handle_size - scale_factor],
            fill=self.handle_color,
            outline="black",
            width=scale_factor * 3
        )
        self.handle_image_resized = large_handle_image.resize((self.height - 4, self.height - 4), Image.LANCZOS)

    def get_knob_position(self):
        """Get the x-coordinate for the knob based on the current state."""
        return self.width - self.height + 3 if self.on else 3

    def toggle(self, event=None):
        """Toggle the switch state and run the animation."""
        self.set(not self.on)  # Toggle the switch state

    def set(self, state):
        """Set the switch to a specific state (True for ON, False for OFF)."""
        if state != self.on:
            self.on = state
            # Use grey for OFF state background, and fg_color for ON state
            new_color = self.fg_color if self.on else self.bg_color  # Grey color for OFF
            self.create_pill_background(new_color)
            self.switch_bg = ImageTk.PhotoImage(self.pill_image)
            self.canvas.itemconfig(self.pill_item, image=self.switch_bg)
            self.animate_switch()

            if self.command:
                self.command()  # Execute the command whenever state changes


    def animate_switch(self):
        """Animate the switch handle sliding effect."""
        y_center = (self.height - self.handle_image_resized.height) // 2
        start_pos = self.canvas.coords(self.handle)[0]
        end_pos = self.get_knob_position()
        duration = 300
        steps = 30
        step_duration = duration // steps

        def ease_out(t):
            return 1 - (1 - t) ** 3

        def move(step):
            if step <= steps:
                t = step / steps
                eased_t = ease_out(t)
                current_pos = start_pos + (end_pos - start_pos) * eased_t
                self.canvas.coords(self.handle, current_pos, y_center)
                self.after(step_duration, move, step + 1)

        move(0)

    def get(self):
        """Get the current state of the switch."""
        return self.on
    
    def update_theme(self):
        """Update the theme and re-render the switch to reflect the parent frame’s color."""
        self.switch_bg_color = self.get_parent_color()
        # Update the canvas background directly
        self.canvas.config(bg=self.switch_bg_color)
        # Re-render the switch with the correct color for the OFF state or ON state
        self.create_pill_background(self.fg_color if self.on else self.bg_color)
        self.switch_bg = ImageTk.PhotoImage(self.pill_image)
        self.canvas.itemconfig(self.pill_item, image=self.switch_bg)

