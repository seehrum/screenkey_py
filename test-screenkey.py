import sys
import logging
import os
import tkinter as tk
from pynput import mouse, keyboard
from threading import Thread, Event, Timer

# Platform-specific configuration for handling key mappings or other features
if sys.platform == "win32":
    platform_name = "Windows"
    # Key mappings specific to Windows
    special_key_cmd = keyboard.Key.cmd
elif sys.platform == "linux":
    platform_name = "Linux"
    # Key mappings specific to Linux (Windows key is sometimes called "Super")
    special_key_cmd = keyboard.Key.alt  # You can replace this with the actual key for the Linux Windows key
else:
    platform_name = "Unknown"

# Configuration settings
CONFIG = {
    "font_size": 16,
    "font_bold": True,
    "window_width": 300,
    "window_height": 100,
    "window_x_position": 300,
    "window_y_position": 300,
    "text_color": "#FFFFFF",
    "background_color": "#000000",
    "uppercase": True,  # Option to always log uppercase
    "log_case_sensitive": False,  # New option to log exact case
    "always_on_top": True,
    "enable_logging": True,
    "log_file": os.path.join(os.getcwd(), "key_log.txt"),
    "font_type": "Arial",
    "clear_text": False,
    "clear_text_duration": 5
}

# Configure logging
if CONFIG["enable_logging"]:
    logging.basicConfig(
        filename=CONFIG["log_file"],
        level=logging.INFO,
        format='%(asctime)s: [%(levelname)s] %(message)s'
    )

class ListenerThread(Thread):
    """
    A thread class for listening to keyboard and mouse events.
    """
    def __init__(self, update_method, stop_event):
        super().__init__()
        self.update_method = update_method
        self.stop_event = stop_event
        self.special_keys = set()
        self.caps_lock_on = False  # Track the Caps Lock state
        self.shift_pressed = False  # Track if Shift is pressed
        self.special_key_map = self.get_special_keys()
        self.mouse_action_map = self.get_mouse_actions()

    def get_special_keys(self):
        """
        Maps special keyboard keys to their string representations.
        """
        return {
            keyboard.Key.space: 'Spacebar',
            keyboard.Key.left: 'Left Arrow',
            keyboard.Key.right: 'Right Arrow',
            keyboard.Key.up: 'Up Arrow',
            keyboard.Key.down: 'Down Arrow',
            keyboard.Key.shift: 'Shift',
            keyboard.Key.shift_r: 'Right Shift',
            keyboard.Key.ctrl: 'Control',
            keyboard.Key.ctrl_r: 'Right Control',
            keyboard.Key.alt: 'Alt',
            keyboard.Key.alt_r: 'Right Alt',
            keyboard.Key.menu: 'Menu',
            special_key_cmd: f'{platform_name} Key',
            keyboard.Key.esc: 'Esc',
            keyboard.Key.tab: 'Tab',
            keyboard.Key.caps_lock: 'Caps Lock',
            keyboard.Key.f1: 'F1',
            keyboard.Key.f2: 'F2',
            keyboard.Key.f3: 'F3',
            keyboard.Key.f4: 'F4',
            keyboard.Key.f5: 'F5',
            keyboard.Key.f6: 'F6',
            keyboard.Key.f7: 'F7',
            keyboard.Key.f8: 'F8',
            keyboard.Key.f9: 'F9',
            keyboard.Key.f10: 'F10',
            keyboard.Key.f11: 'F11',
            keyboard.Key.f12: 'F12',
            keyboard.Key.backspace: 'Backspace',
            keyboard.Key.enter: 'Enter',
            keyboard.Key.delete: 'Delete',
            keyboard.Key.home: 'Home',
            keyboard.Key.page_up: 'Page Up',
            keyboard.Key.page_down: 'Page Down',
            keyboard.Key.end: 'End',
            keyboard.Key.num_lock: 'Num Lock',
            keyboard.Key.insert: 'Insert',
            keyboard.Key.print_screen: 'Print Screen',
            keyboard.Key.scroll_lock: 'Scroll Lock',
            keyboard.Key.pause: 'Pause',
        }

    def get_mouse_actions(self):
        return {
            'Button.left': 'Left Click',
            'Button.right': 'Right Click',
            'Button.middle': 'Middle Click',
            'Scroll up': 'Scroll Up',
            'Scroll down': 'Scroll Down',
        }

    def run(self):
        try:
            with keyboard.Listener(on_press=self.on_press,
                                   on_release=self.on_release) as keyboard_listener, \
                 mouse.Listener(on_click=self.on_click,
                                on_scroll=self.on_scroll) as mouse_listener:
                while not self.stop_event.is_set():
                    self.stop_event.wait(0.1)
        except Exception as e:
            logging.error(f"Listener thread encountered an error: {e}")

    def on_press(self, key):
        """
        Handles the on_press event for keyboard keys.
        """
        try:
            key_info = self.get_key_info(key)

            # Handle shift, ctrl, alt key presses
            if key in {keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.alt, special_key_cmd, keyboard.Key.alt_r}:
                self.special_keys.add(key_info)
                special_keys_combination = ' + '.join(sorted(self.special_keys))

                # Ensure special keys are shown in uppercase
                if CONFIG["uppercase"]:
                    special_keys_combination = special_keys_combination.upper()

                self.update_method(special_keys_combination)  # Display special key pressed alone
                if CONFIG["enable_logging"]:
                    logging.info(f"Key pressed: {special_keys_combination}")

            else:
                # Combine special keys (if any) with the current key pressed
                combined_keys = ' + '.join(sorted(self.special_keys) + [key_info])
                display_text = self.process_key_case(combined_keys)
                self.update_method(display_text)

                if CONFIG["enable_logging"]:
                    log_text = self.process_key_case(combined_keys, logging_mode=True)
                    logging.info(f"Key pressed: {log_text}")

            # Handle caps lock
            if key == keyboard.Key.caps_lock:
                self.caps_lock_on = not self.caps_lock_on

        except Exception as e:
            logging.error(f"Error in on_press: {e}")

    def on_release(self, key):
        """
        Handles the on_release event for keyboard keys.
        """
        try:
            key_info = self.get_key_info(key)
            if key_info in self.special_keys:
                self.special_keys.remove(key_info)

        except Exception as e:
            logging.error(f"Error in on_release: {e}")

    def on_click(self, x, y, button, pressed):
        """
        Handles the on_click event for mouse buttons.
        """
        try:
            if pressed:
                button_info = self.mouse_action_map.get(str(button), str(button))
                
                # Ensure mouse button info is shown in uppercase
                if CONFIG["uppercase"]:
                    button_info = button_info.upper()

                self.update_method(button_info)
                if CONFIG["enable_logging"]:
                    logging.info(f"Mouse clicked: {button_info}")
        except Exception as e:
            logging.error(f"Error in on_click: {e}")

    def on_scroll(self, x, y, dx, dy):
        """
        Handles the on_scroll event for mouse scrolling.
        """
        try:
            direction = 'Scroll up' if dy > 0 else 'Scroll down'
            scroll_info = self.mouse_action_map.get(direction, direction)

            # Ensure scroll info is shown in uppercase
            if CONFIG["uppercase"]:
                scroll_info = scroll_info.upper()

            self.update_method(scroll_info)
            if CONFIG["enable_logging"]:
                logging.info(f"Mouse scrolled: {scroll_info}")
        except Exception as e:
            logging.error(f"Error in on_scroll: {e}")

    def get_key_info(self, key):
        """
        Retrieves string representation for a given keyboard key.
        """
        # Add virtual key codes for numpad keys on Windows
        numpad_key_map = {
            keyboard.KeyCode.from_vk(96): '0',
            keyboard.KeyCode.from_vk(97): '1',
            keyboard.KeyCode.from_vk(98): '2',
            keyboard.KeyCode.from_vk(99): '3',
            keyboard.KeyCode.from_vk(100): '4',
            keyboard.KeyCode.from_vk(101): '5',
            keyboard.KeyCode.from_vk(102): '6',
            keyboard.KeyCode.from_vk(103): '7',
            keyboard.KeyCode.from_vk(104): '8',
            keyboard.KeyCode.from_vk(105): '9',
            keyboard.KeyCode.from_vk(106): '*',
            keyboard.KeyCode.from_vk(107): '+',
            keyboard.KeyCode.from_vk(109): '-',
            keyboard.KeyCode.from_vk(110): '.',
            keyboard.KeyCode.from_vk(111): '/',
        }

        # Handle numpad key mapping for Windows
        if key in numpad_key_map:
            return numpad_key_map[key]

        # Handle special keys
        if key in self.special_key_map:
            return self.special_key_map[key]

        # Handle regular character keys
        try:
            return key.char if key.char is not None else key.name
        except AttributeError:
            # Handle unknown key (such as <97> issue)
            return f"<{key.vk}>" if hasattr(key, 'vk') else str(key)

    def process_key_case(self, key_info, logging_mode=False):
        """
        Processes the key case (uppercase/lowercase) based on the configuration and whether logging or display is involved.
        """
        if CONFIG["log_case_sensitive"]:
            # Determine if the key should be uppercase or lowercase
            is_upper = self.shift_pressed != self.caps_lock_on
            case_indicator = "UP" if is_upper else "LO"
            key_info = key_info.upper() if is_upper else key_info.lower()
            if logging_mode:
                return f"{key_info} ({case_indicator})"  # Add case info only to the log
            return key_info
        else:
            # If CONFIG["uppercase"] is True, make all keys uppercase
            return key_info.upper() if CONFIG["uppercase"] else key_info


class ScreenkeyApp(tk.Tk):
    """
    Main application class for Screenkey using Tkinter.
    """
    def __init__(self):
        super().__init__()
        self.clear_timer = None
        self.init_ui()
        self.stop_event = Event()
        self.listener_thread = ListenerThread(self.update_display, self.stop_event)
        self.listener_thread.start()

    def init_ui(self):
        self.geometry(f"{CONFIG['window_width']}x{CONFIG['window_height']}+{CONFIG['window_x_position']}+{CONFIG['window_y_position']}")
        self.title('Screenkey v3.3')
        if CONFIG["always_on_top"]:
            try:
                self.attributes('-topmost', True)
            except tk.TclError:
                logging.warning(f"Always on top may not work on {platform_name}")

        self.label = tk.Label(self, text="",
                              font=(CONFIG["font_type"], CONFIG["font_size"],
                                    "bold" if CONFIG["font_bold"] else "normal"))
        self.label.pack(expand=True)

        self.configure(bg=CONFIG["background_color"])
        self.label.configure(fg=CONFIG["text_color"], bg=CONFIG["background_color"])

    def update_display(self, text):
        if not self.stop_event.is_set():
            self.label.config(text=text)

            if CONFIG["clear_text"]:
                if self.clear_timer is not None:
                    self.clear_timer.cancel()
                self.clear_timer = Timer(CONFIG["clear_text_duration"], self.clear_display)
                self.clear_timer.start()

    def clear_display(self):
        self.label.config(text="")

    def on_close(self):
        self.stop_event.set()
        self.listener_thread.join()
        if self.clear_timer is not None:
            self.clear_timer.cancel()
        self.destroy()


if __name__ == '__main__':
    try:
        app = ScreenkeyApp()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
