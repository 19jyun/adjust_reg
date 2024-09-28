# animated_switch.py
import customtkinter as ctk
import tkinter as tk

class AnimatedSwitch(ctk.CTkFrame):
    def __init__(self, parent, width=80, height=30, bg_color="gray", fg_color="green", handle_color="white", command=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.handle_color = handle_color
        self.command = command  # Function to call when toggled

        # Create a canvas to hold the custom switch
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, bg=self.bg_color)
        self.canvas.pack()

        # Draw the pill-shaped background and the handle
        self.bg_rect = self.canvas.create_oval(0, 0, self.width, self.height, fill=self.bg_color, outline="")
        self.handle = self.canvas.create_oval(2, 2, self.height - 2, self.height - 2, fill=self.handle_color, outline="")

        # State tracking
        self.on = False
        self.switch_active = False  # To avoid multiple toggles during animation

        # Bind click event to toggle the switch
        self.canvas.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        """Toggle the switch animation on click."""
        if not self.switch_active:
            self.on = not self.on
            self.switch_active = True
            self.animate_switch()
            # Execute the command callback if provided
            if self.command:
                self.command()  # Call the function whenever toggled

    def animate_switch(self):
        """Animate the switch handle with ease-out effect."""
        start_pos = 2 if self.on else self.width - self.height + 2
        end_pos = self.width - self.height + 2 if self.on else 2
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
                self.canvas.coords(self.handle, current_pos, 2, current_pos + self.height - 4, self.height - 2)
                self.after(step_duration, move, step + 1)
            else:
                self.switch_active = False

        move(0)

if __name__ == "__main__":
    def on_toggle():
        print("Switch toggled")

    root = tk.Tk()
    switch = AnimatedSwitch(root, command=on_toggle)
    switch.pack(pady=10)
    root.mainloop()