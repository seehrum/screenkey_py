import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from pynput import mouse, keyboard

# Global Constants for Customization
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
    "font_type": "Arial"  # Added font type to CONFIG
}

# Configure logging
if CONFIG["enable_logging"]:
    logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO, format='%(asctime)s: %(message)s')

class ListenerThread(QThread):
    keyPressed = pyqtSignal(str)
    mouseAction = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.special_keys = set()
        self.special_key_map = self.get_special_keys()
        self.mouse_action_map = self.get_mouse_actions()

    def get_special_keys(self):
        # Returns a dictionary mapping special keys to their descriptions
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
        # Returns a dictionary mapping mouse actions to their descriptions
        return {
            'Button.left': 'Left Click',
            'Button.right': 'Right Click',
            'Button.middle': 'Middle Click',
            'Scroll up': 'Scroll Up',
            'Scroll down': 'Scroll Down',
            # Additional mappings as needed
        }

    def run(self):
        # Main method to start listeners for keyboard and mouse events
        try:
            def get_key_info(key):
                # Retrieves information about the key
                if key in self.special_key_map:
                    return self.special_key_map[key]
                try:
                    return key.char if key.char is not None else key.name
                except AttributeError:
                    return str(key)

            def on_press(key):
                # Handles key press events
                key_info = get_key_info(key)
                if key in {keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt}:
                    self.special_keys.add(key_info)
                else:
                    key_info = ' + '.join(sorted(self.special_keys) + [key_info])

                if CONFIG["uppercase"]:
                    key_info = key_info.upper()

                self.keyPressed.emit(key_info)
                if CONFIG["enable_logging"]:
                    logging.info(f"Key pressed: {key_info}")

            def on_release(key):
                # Handles key release events
                key_info = get_key_info(key)
                if key_info in self.special_keys:
                    self.special_keys.remove(key_info)

            def on_click(x, y, button, pressed):
                # Handles mouse click events
                if pressed:
                    button_info = self.mouse_action_map.get(str(button), str(button))
                    self.mouseAction.emit(button_info.upper() if CONFIG["uppercase"] else button_info)
                    if CONFIG["enable_logging"]:
                        logging.info(f"Mouse clicked: {button_info}")

            def on_scroll(x, y, dx, dy):
                # Handles mouse scroll events
                direction = 'Scroll up' if dy > 0 else 'Scroll down'
                scroll_info = self.mouse_action_map.get(direction, direction)
                self.mouseAction.emit(scroll_info.upper() if CONFIG["uppercase"] else scroll_info)
                if CONFIG["enable_logging"]:
                    logging.info(f"Mouse scrolled: {scroll_info}")

            # Start listeners
            with keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener, \
                 mouse.Listener(on_click=on_click, on_scroll=on_scroll) as mouse_listener:
                keyboard_listener.join()
                mouse_listener.join()
        except Exception as e:
            # Logging any exceptions in the listener thread
            logging.error(f"Error in listener thread: {e}")

class ScreenkeyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Initialize the UI elements of the application
        try:
            self.setGeometry(CONFIG["window_x_position"], CONFIG["window_y_position"],
                             CONFIG["window_width"], CONFIG["window_height"])
            self.setWindowTitle('Screenkey')
            self.setWindowFlags(Qt.WindowStaysOnTopHint if CONFIG["always_on_top"] else Qt.Widget)

            self.label = QLabel(self)
            font = QFont(CONFIG["font_type"], CONFIG["font_size"])
            font.setBold(CONFIG["font_bold"])
            self.label.setFont(font)
            self.label.setAlignment(Qt.AlignCenter)

            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(CONFIG["background_color"]))
            palette.setColor(QPalette.WindowText, QColor(CONFIG["text_color"]))
            self.setPalette(palette)

            layout = QHBoxLayout()
            layout.addWidget(self.label)
            self.setLayout(layout)

            self.thread = ListenerThread()
            self.thread.keyPressed.connect(self.update_display)
            self.thread.mouseAction.connect(self.update_display)
            self.thread.start()
        except Exception as e:
            logging.error(f"Error initializing Screenkey UI: {e}")

    def update_display(self, text):
        # Update the display label with the provided text
        self.label.clear()
        self.label.setText(text)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = ScreenkeyApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
