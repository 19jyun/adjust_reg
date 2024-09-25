import keyboard

def on_key_event(event):
    """
    Callback function that is triggered on key press or release events.
    Prints the event details to the terminal.
    """
    # Event.name gives the key name (e.g., 'a', 'enter', 'space')
    # Event.event_type is either 'down' or 'up'
    key_event_type = 'Pressed' if event.event_type == 'down' else 'Released'
    print(f"{event.name.capitalize()} {key_event_type}")

def main():
    """
    Main function to start the keyboard listener.
    """
    print("Listening to keyboard events. Press 'Esc' to stop.")

    # Hook the listener to call 'on_key_event' when a key is pressed or released
    keyboard.hook(on_key_event)

    # Block the main thread until 'Esc' is pressed
    keyboard.wait('esc')

if __name__ == "__main__":
    main()
