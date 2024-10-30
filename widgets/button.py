import customtkinter as ctk

class BouncingButton(ctk.CTkButton):
    def __init__(self, parent, text="Bounce!", duration=75, command=None, *args, **kwargs):
        # Omit fg_color and hover_color to use default CTkButton colors
        super().__init__(parent, text=text, *args, **kwargs)

        self.duration = duration
        self.steps = 30
        self.command = command
        self.original_width = self._current_width
        self.original_height = self._current_height
        self.bounce_scale = 1.1
        self.state = "normal"

        # Bind the click event
        self.bind("<Button-1>", self.start_bounce)

    def configure(self, **kwargs):
        """Override configure method to handle state changes."""
        if "state" in kwargs:
            self.state = kwargs.pop("state")
            if self.state == "disabled":
                # Use default disabled colors from CTkButton
                super().configure(state="disabled")
                self.unbind("<Button-1>")
            else:
                # Restore to default enabled state colors
                super().configure(state="normal")
                self.bind("<Button-1>", self.start_bounce)

        super().configure(**kwargs)

    def start_bounce(self, event=None):
        if self.state == "normal":
            self.bounce(step=0)

    def bounce(self, step):
        if step < self.steps:
            t = step / self.steps
            scale_factor = 1 - (self.bounce_scale - 1) * self.ease_out(t) if step < self.steps // 2 else \
                           1 - (self.bounce_scale - 1) * self.ease_out(1 - t)
            
            new_width = int(self.original_width * scale_factor)
            new_height = int(self.original_height * scale_factor)
            self.configure(width=new_width, height=new_height)

            self.after(self.duration // self.steps, self.bounce, step + 1)
        else:
            self.configure(width=self.original_width, height=self.original_height)
            if self.command and self.state == "normal":
                self.command()

    def ease_out(self, t):
        return 1 - (1 - t) ** 6
