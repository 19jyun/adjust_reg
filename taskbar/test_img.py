import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import numpy as np
import os

class TestImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set window title
        self.title("Dynamic Image Cropping (Width Only)")
        self.geometry("600x500")

        # Image path (make sure this image exists in the taskbar directory)
        self.image_path = "taskbar/background_image.png"

        # Load image using PIL (ensure that the image file exists)
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image not found at path: {self.image_path}")

        self.original_image = Image.open(self.image_path)
        self.original_image_array = np.array(self.original_image)

        # Initial Image Size
        self.image_width = self.original_image_array.shape[1]
        self.image_height = self.original_image_array.shape[0]

        # Variable to control slider delay
        self.slider_event_id = None

        # Create GUI layout with CustomTkinter
        self.setup_ui()

    def setup_ui(self):
        # Create a frame to hold everything
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a slider to adjust image width percentage (0-100)
        self.slider = ctk.CTkSlider(self.main_frame, from_=0, to=100, command=self.on_slider_change)
        self.slider.pack(fill="x", padx=20, pady=10)
        self.slider.set(100)  # Set slider to 100% initially

        # Create a figure and axis for displaying the image
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.ax.axis('off')  # Turn off axes

        # Embed the matplotlib figure into the Tkinter window (initialize the canvas here)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        # Display the initial image at 100% width
        self.display_image(100)

    def display_image(self, scale_percentage):
        """Display the image according to the slider percentage by cropping only the width."""
        crop_width = int(self.image_width * (scale_percentage / 100.0))  # Calculate the width to crop

        # Crop the image width (height remains the same)
        cropped_image = self.original_image.crop((0, 0, crop_width, self.image_height))
        cropped_image_array = np.array(cropped_image)

        # Clear the previous image and display the cropped one
        self.ax.clear()
        self.ax.imshow(cropped_image_array)
        self.ax.axis('off')
        self.canvas.draw_idle()  # Redraw the canvas to reflect changes

    def on_slider_change(self, value):
        """Callback function when the slider value changes"""
        # If there's already a pending event, cancel it
        if self.slider_event_id is not None:
            self.after_cancel(self.slider_event_id)

        # Schedule a new event after 50ms to update the image
        self.slider_event_id = self.after(50, lambda: self.display_image(float(value)))

if __name__ == "__main__":
    # Create and run the app
    app = TestImageApp()
    app.mainloop()
