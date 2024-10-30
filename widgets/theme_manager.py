# theme_manager.py
theme_change_callbacks = []

def register_theme_change_callback(callback):
    """Register a callback to be called on theme change."""
    theme_change_callbacks.append(callback)

def trigger_theme_change():
    """Call all registered theme change callbacks."""
    for callback in theme_change_callbacks:
        callback()
