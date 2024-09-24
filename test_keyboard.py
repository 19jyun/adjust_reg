import ctypes
from ctypes import wintypes
import threading

# Define the KBDLLHOOKSTRUCT structure
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG),
    ]

# Define the callback function type
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)

# Callback function for the low-level keyboard hook
@LowLevelKeyboardProc
def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode == 0:  # HC_ACTION, we process the event
        kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT))
        vkCode = kbd.contents.vkCode
        scanCode = kbd.contents.scanCode
        print(f"Key Pressed: vkCode={vkCode}, scanCode={scanCode}")
    
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

# Install the keyboard hook
def install_hook():
    WH_KEYBOARD_LL = 13
    module_handle = ctypes.windll.kernel32.GetModuleHandleW(None)
    if not module_handle:
        print("Failed to get module handle")
        return None

    keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        low_level_keyboard_proc,
        module_handle,
        0
    )
    if not keyboard_hook:
        print("Failed to install hook")
    else:
        print("Hook installed successfully")
    return keyboard_hook

# Run the hook in a separate thread
def run_hook():
    hook_id = install_hook()
    if hook_id:
        ctypes.windll.user32.GetMessageA(None, 0, 0, 0)  # Keep the hook running

# Main function to start the program
if __name__ == "__main__":
    hook_thread = threading.Thread(target=run_hook)
    hook_thread.start()
    hook_thread.join()