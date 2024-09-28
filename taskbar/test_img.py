import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

img_path = "taskbar/background_image.png"

def display_image(img_path):
    root = ctk.CTk()
    root.title("Image Display")

    # Load image using PIL
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image not found at path: {img_path}")

    img = Image.open(img_path)
    tk_img = ImageTk.PhotoImage(img)

    # Create a CTkLabel to display the image
    img_label = ctk.CTkLabel(root, image=tk_img)
    img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.mainloop()

display_image(img_path)