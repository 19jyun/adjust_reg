import customtkinter as ctk
from tkinter import Tk
from widgets.sliding_frames import SlidingFrame  # Assuming your SlidingFrame class is saved in sliding_frames.py

def main():
    # Create the main Tkinter root window
    root = Tk()
    root.geometry("800x600")  # Set the main window size
    root.title("Sliding Frame Test")

    # Create a CustomTkinter container frame inside the main window
    container = ctk.CTkFrame(root, width=800, height=600)
    container.pack(expand=True, fill="both")

    # Create a sliding frame with specific dimensions
    sliding_frame = SlidingFrame(container, width = 10, height = 10)
    
    # Button to trigger the slide in and out
    toggle_button = ctk.CTkButton(container, text="Toggle Sliding Frame", 
                                  command=lambda: toggle_frame(sliding_frame))
    toggle_button.pack(pady=20)

    # btn1 = ctk.CTkButton(sliding_frame, text="Button 1")
    # btn1.pack(pady=10)
    # btn2 = ctk.CTkButton(sliding_frame, text="Button 2")
    # btn2.pack(pady=10)
    # btn3 = ctk.CTkButton(sliding_frame, text="Button 3")
    # btn3.pack(pady=10)
    # btn4 = ctk.CTkButton(sliding_frame, text="Button 4")
    # btn4.pack(pady=10)
    # btn5 = ctk.CTkButton(sliding_frame, text="Button 5")
    # btn5.pack(pady=10)

    # Run the main loop
    root.mainloop()

def toggle_frame(frame):
    """Toggle the visibility of the sliding frame."""
    if not frame.is_visible:
        frame.pack()
    else:
        frame.pack_forget()

if __name__ == "__main__":
    main()
