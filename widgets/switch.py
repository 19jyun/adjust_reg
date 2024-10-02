import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import pywinstyles
class AnimatedSwitch(ctk.CTkFrame):
    def __init__(self, parent, width=80, height=30, bg_color="gray", fg_color="lime", handle_color="white", command=None):
        super().__init__(parent, fg_color=bg_color)
        
        parent_bg_color = self.collect_color_info(parent)
        
        self.width = width
        self.height = height
        self.bg_color = bg_color  # Color when off
        self.fg_color = fg_color  # Color when on
        self.parent_bg_color = parent_bg_color
        self.handle_color = handle_color
        self.command = command  # Function to call when toggled

        # State tracking
        self.on = False
        
        # Create the images for both states (on and off)
        self.create_pill_background(self.bg_color)  # Initial state is off
        self.create_handle_image()

        # Create a transparent canvas to hold the custom switch
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, bg=self.parent_bg_color)
        self.canvas.pack()

        # Create a transparent background image for the canvas
        self.create_transparent_background()
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

        self.switch_active = False  # To avoid multiple toggles during animation

        # Bind click event to toggle the switch
        self.canvas.bind("<Button-1>", self.toggle)

    def get_parent_bg_color(self, parent):
        """Get the background color of the parent widget."""
        try:
            bg = parent.cget("fg_color") if isinstance(parent, ctk.CTkBaseClass) else parent.cget("bg")
        except:
            bg = "#FFFFFF"  # Default to white if not available
        return bg

    def collect_color_info(self, widget):
        """Collect the background color based on widget type."""
        try:
            if isinstance(widget, ctk.CTkBaseClass):
                colors = widget.cget("fg_color")
                if isinstance(colors, str):
                    return colors
                elif isinstance(colors, list) and len(colors) == 2:
                    appearance_mode = ctk.get_appearance_mode()
                    return colors[0] if appearance_mode == "Light" else colors[1]
                else:
                    return "#FFFFFF"
            elif isinstance(widget, (tk.Tk, tk.Frame, tk.Canvas, tk.Toplevel)):
                return widget.cget("bg")
            else:
                return "#FFFFFF"
        except Exception as e:
            return "#FFFFFF"

    def create_pill_background(self, color):
        """Create a rounded pill-shaped image with a transparent background for the switch."""
        scale_factor = 4
        large_width, large_height = self.width * scale_factor, self.height * scale_factor
        large_pill_image = Image.new("RGBA", (large_width, large_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(large_pill_image)
        large_radius = self.height // 2 * scale_factor
        draw.rounded_rectangle(
            [0, 0, large_width, large_height],
            radius=large_radius,
            fill=color,
            outline="black",
            width=scale_factor * 3
        )
        self.pill_image = large_pill_image.resize((self.width, self.height), Image.LANCZOS)

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
        self.handle_image_resized = large_handle_image.resize((self.height, self.height), Image.LANCZOS)

    def create_transparent_background(self):
        """Create a fully transparent image to use as the canvas background."""
        self.transparent_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

    def toggle(self, event=None):
        """Toggle the switch animation on click and update the background color."""
        self.set(not self.on)  # Use set method to toggle the switch

    def set(self, state):
        """Set the switch to a specific state (True for 'on', False for 'off')."""
        if state != self.on:  # Only toggle if the state is different
            self.on = state
            new_color = self.fg_color if self.on else self.bg_color
            self.create_pill_background(new_color)
            self.switch_bg = ImageTk.PhotoImage(self.pill_image)
            self.canvas.itemconfig(self.pill_item, image=self.switch_bg)
            self.animate_switch()

            if self.command:
                self.command()  # Execute the command whenever state changes

    def animate_switch(self):
        """Animate the switch handle with ease-out effect."""
        y_center = (self.height - self.handle_image_resized.height) // 2
        border_width = 3
        left_pos = border_width
        right_pos = self.width - self.height - border_width
        current_pos = self.canvas.coords(self.handle)[0]
        start_pos = current_pos
        end_pos = right_pos if self.on else left_pos
        duration = 300
        steps = 30
        step_duration = duration // steps

        def ease_out(t):
            return 1 - (1 - t) ** 3

        def move(step):
            nonlocal start_pos
            if step <= steps:
                t = step / steps
                eased_t = ease_out(t)
                current_pos = start_pos + (end_pos - start_pos) * eased_t
                self.canvas.coords(self.handle, current_pos, y_center)
                self.after(step_duration, move, step + 1)
            else:
                self.switch_active = False

        move(0)

    def get(self):
        """Get the current state of the switch."""
        return self.on
