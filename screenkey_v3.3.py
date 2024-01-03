import sys
import logging
import tkinter as tk
from pynput import mouse, keyboard
from threading import Thread, Event

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
    "uppercase": True,
    "always_on_top": True,
    "enable_logging": True,
    "log_file": "key_log.txt",
    "font_type": "Arial"
}

# Configure logging
if CONFIG["enable_logging"]:
    logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO, format='%(asctime)s: %(message)s')

class ListenerThread(Thread):
    """
    A thread class for listening to keyboard and mouse events.
    """
    def __init__(self, update_method, stop_event):
        super().__init__()
        self.update_method = update_method
        self.stop_event = stop_event
        self.special_keys = set()
        self.special_key_map = self.get_special_keys()
        self.mouse_action_map = self.get_mouse_actions()

    def get_special_keys(self):
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
            keyboard.Key.cmd: 'Windows key',
            keyboard.Key.cmd_r: 'Right Windows key',
            keyboard.Key.esc: 'Esc',
            keyboard.Key.tab: 'Tab',
            keyboard.Key.caps_lock: 'Caps lock key',
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
            keyboard.KeyCode.from_vk(65437): '5',
            keyboard.KeyCode.from_vk(65027): 'AltGr',
            keyboard.KeyCode.from_vk(65511): 'Alt',
            keyboard.KeyCode.from_vk(65439): ',',
            keyboard.KeyCode.from_vk(65452): ',',
        }

    def get_mouse_actions(self):
        return {
            'Button.left': 'Left Click',
            'Button.right': 'Right Click',
            'Button.middle': 'Middle Click',
            'Scroll up': 'Scroll Up',
            'Scroll down': 'Scroll Down',
            # ... Add other mouse actions as needed
        }

    def run(self):
        def get_key_info(key):
            if key in self.special_key_map:
                return self.special_key_map[key]
            try:
                return key.char if key.char is not None else key.name
            except AttributeError:
                return str(key)

        def on_press(key):
            key_info = get_key_info(key)
            if key in {keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt}:
                self.special_keys.add(key_info)
            else:
                valid_keys = [k for k in self.special_keys if k]
                key_info = ' + '.join(sorted(valid_keys) + [key_info])

            if CONFIG["uppercase"]:
                key_info = key_info.upper()

            self.update_method(key_info)
            if CONFIG["enable_logging"]:
                logging.info(f"Key pressed: {key_info}")

        def on_release(key):
            key_info = get_key_info(key)
            if key_info in self.special_keys:
                self.special_keys.remove(key_info)

        def on_click(x, y, button, pressed):
            if pressed:
                button_info = self.mouse_action_map.get(str(button), str(button))
                if CONFIG["uppercase"]:
                    button_info = button_info.upper()
                self.update_method(button_info)
                if CONFIG["enable_logging"]:
                    logging.info(f"Mouse clicked: {button_info}")

        def on_scroll(x, y, dx, dy):
            direction = 'Scroll up' if dy > 0 else 'Scroll down'
            scroll_info = self.mouse_action_map.get(direction, direction)
            if CONFIG["uppercase"]:
                scroll_info = scroll_info.upper()
            self.update_method(scroll_info)
            if CONFIG["enable_logging"]:
                logging.info(f"Mouse scrolled: {scroll_info}")

        with keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener, \
             mouse.Listener(on_click=on_click, on_scroll=on_scroll) as mouse_listener:
            while not self.stop_event.is_set():
                self.stop_event.wait(0.1)

class ScreenkeyApp(tk.Tk):
    """
    Main application class for Screenkey using Tkinter.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.stop_event = Event()
        self.listener_thread = ListenerThread(self.update_display, self.stop_event)
        self.listener_thread.start()

    def init_ui(self):
        self.geometry(f"{CONFIG['window_width']}x{CONFIG['window_height']}+{CONFIG['window_x_position']}+{CONFIG['window_y_position']}")
        self.title('Screenkey')
        if CONFIG["always_on_top"]:
            self.attributes('-topmost', True)

        self.label = tk.Label(self, text="", font=(CONFIG["font_type"], CONFIG["font_size"], "bold" if CONFIG["font_bold"] else "normal"))
        self.label.pack(expand=True)

        self.configure(bg=CONFIG["background_color"])
        self.label.configure(fg=CONFIG["text_color"], bg=CONFIG["background_color"])

    def update_display(self, text):
        if not self.stop_event.is_set():
            self.label.config(text=text)

    def on_close(self):
        self.stop_event.set()
        self.listener_thread.join()
        self.destroy()

if __name__ == '__main__':
    try:
        app = ScreenkeyApp()
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        app.mainloop()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
