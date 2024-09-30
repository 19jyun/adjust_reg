import customtkinter as ctk
import tkinter as tk
from typing import Union, Tuple, Callable, List, Optional, Any


class AnimatedDropdownMenu(ctk.CTkFrame):
    def __init__(self,
                 master: Any,
                 width: int = 140,
                 height: int = 30,
                 corner_radius: Optional[int] = None,
                 border_width: Optional[int] = None,
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
                 font: Optional[Union[tuple, ctk.CTkFont]] = None,
                 dropdown_font: Optional[Union[tuple, ctk.CTkFont]] = None,
                 values: Optional[List[str]] = None,
                 state: str = tk.NORMAL,
                 variable: Union[tk.Variable, None] = None,
                 command: Union[Callable[[str], Any], None] = None,
                 justify: str = "left",
                 **kwargs):
        
        # Initialize parent class
        super().__init__(master=master, fg_color=fg_color, width=width, height=height, **kwargs)

        # Assign initial properties
        self._corner_radius = 6 if corner_radius is None else corner_radius
        self._border_width = 2 if border_width is None else border_width
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._border_color = border_color or "#D9D9D9"
        self._button_color = button_color or "#3B3B3B"
        self._button_hover_color = button_hover_color or "#565656"
        self._dropdown_fg_color = dropdown_fg_color or "#343638"
        self._dropdown_hover_color = dropdown_hover_color or "#3A3A3A"
        self._dropdown_text_color = dropdown_text_color or "#FFFFFF"
        self._text_color = text_color or "#FFFFFF"
        self._text_color_disabled = text_color_disabled or "#A9A9A9"
        self._font = ctk.CTkFont() if font is None else font
        self._command = command
        self._variable = variable
        self._values = values if values else ["Option 1", "Option 2", "Option 3"]
        self.is_open = False  # Track if the dropdown is open

        # Create the dropdown button with matching CTkComboBox aesthetics
        self.menu_button = ctk.CTkButton(
            self, text="Select an Option",
            width=width,
            height=height,
            fg_color=self._button_color,
            text_color=self._text_color,
            hover_color=self._button_hover_color,
            border_width=self._border_width,
            border_color=self._border_color,
            corner_radius=self._corner_radius,
            command=self.toggle_menu
        )
        self.menu_button.pack(padx=10, pady=5)

        # Container for dropdown items
        self.menu_frame = ctk.CTkFrame(
            self, fg_color=self._dropdown_fg_color, width=width, height=0,
            border_width=self._border_width, border_color=self._border_color
        )
        self.menu_frame.pack_propagate(False)  # Prevent automatic resizing
        self.menu_frame.pack(padx=10, pady=(0, 5), anchor="nw")

        # Create dropdown items
        self.items = []
        for option in self._values:
            item = ctk.CTkButton(
                self.menu_frame, text=option,
                width=width - 10,
                height=height,
                fg_color=self._dropdown_fg_color,
                text_color=self._dropdown_text_color,
                hover_color=self._dropdown_hover_color,
                border_width=1, border_color=self._border_color,
                command=lambda opt=option: self.select_option(opt)
            )
            item.pack(pady=0, padx=5)
            item.place(y=-height)  # Place items out of view initially
            self.items.append(item)

    def toggle_menu(self):
        """Open or close the dropdown menu."""
        if self.is_open:
            self.close_menu()
        else:
            self.open_menu()

    def open_menu(self):
        """Animate the menu items dropping down."""
        self.is_open = True
        total_height = len(self.items) * self.menu_button.cget("height")
        self.menu_frame.configure(height=total_height)  # Set frame height to fit all items

        for idx, item in enumerate(self.items):
            self.animate_item(item, target_y=idx * self.menu_button.cget("height"))

    def close_menu(self):
        """Animate the menu items being absorbed back up."""
        self.is_open = False
        for item in reversed(self.items):
            self.animate_item(item, target_y=-self.menu_button.cget("height"))

        self.after(300, lambda: self.menu_frame.configure(height=0))  # Collapse the menu

    def animate_item(self, item, target_y):
        """Animate a single item to a new y position."""
        duration = 300
        steps = 20
        start_y = item.winfo_y()
        delta_y = (target_y - start_y) / steps

        def step_animation(step=0):
            if step < steps:
                new_y = start_y + delta_y * step
                item.place(y=new_y)
                self.after(15, lambda: step_animation(step + 1))
            else:
                item.place(y=target_y)

        step_animation()

    def select_option(self, option):
        """Update button text and execute callback."""
        self.menu_button.configure(text=option)
        self.close_menu()
        if self._command:
            self._command(option)


if __name__ == "__main__":
    def on_option_selected(option):
        print(f"Selected: {option}")

    root = ctk.CTk()
    root.geometry("300x300")

    dropdown = AnimatedDropdownMenu(root, values=["Option A", "Option B", "Option C"], command=on_option_selected)
    dropdown.pack(pady=20)

    new_dropdown = ctk.CTkComboBox(root, values=["Option 1", "Option 2", "Option 3"], command=on_option_selected)
    new_dropdown.pack(pady=20)

    root.mainloop()
