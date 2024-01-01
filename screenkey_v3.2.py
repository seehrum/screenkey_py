import pygame
import os
import logging
from pygame.locals import QUIT
from pynput import keyboard, mouse
import threading
import time

# Configuration Settings
PROJECT_VERSION = 'Screenkey v3.2'
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 100
FONT_SIZE = 33
BUTTON_FONT_SIZE = 24
ENABLE_LOGGING = False
LOG_FILE = 'input_log.txt'
BUTTON_COLOR = (200, 0, 0)  # Red
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
CLEAR_DELAY = 3600
MIN_KEY_PRESS_INTERVAL = 0.5

def clear_console():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

class InputDisplay:
    """
    A class to display keyboard and mouse inputs on a Pygame window.
    """

    def __init__(self):
        """
        Initializes the InputDisplay with specified parameters.
        """
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.font_size = FONT_SIZE
        self.button_font_size = BUTTON_FONT_SIZE
        self.enable_logging = ENABLE_LOGGING
        self.log_file = LOG_FILE
        self.initialize()

    def initialize(self):
        """
        Initializes the necessary components for the display.
        """
        self.setup_logging()
        self.setup_environment()
        self.initialize_pygame()
        self.initialize_listeners()
        self.initialize_screen_elements()
        clear_console()
        print(PROJECT_VERSION)

    def setup_environment(self):
        """
        Sets up the environment by hiding pygame support prompt.
        """
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

    def setup_logging(self):
        """
        Configures advanced logging.
        """
        if self.enable_logging:
            logging.basicConfig(filename=self.log_file, level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None

    def initialize_pygame(self):
        """
        Initializes Pygame, fonts, and the display screen.
        """
        pygame.init()
        self.font = pygame.font.SysFont(None, self.font_size)
        self.button_font = pygame.font.SysFont(None, self.button_font_size)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Input Display")

    def initialize_listeners(self):
        """
        Initializes keyboard and mouse listeners.
        """
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def initialize_screen_elements(self):
        """
        Initializes screen elements like the close button and control variables.
        """
        self.setup_close_button()
        self.initialize_control_variables()
        self.special_keys = self.get_special_keys()
        self.pygame_clear_screen()

    def setup_close_button(self):
        """
        Sets up the close button's appearance and position.
        """
        self.button_width, self.button_height = 50, 20
        self.button_x, self.button_y = self.screen_width - self.button_width - 10, 10
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_text = self.button_font.render('X', True, TEXT_COLOR)

    def initialize_control_variables(self):
        """
        Initializes control variables for managing the display and input events.
        """
        self.current_text = []
        self.key_pressed = set()
        self.running = True
        self.timer = None
        self.last_key_press_time = 0

    def get_special_keys(self):
        """
        Returns a dictionary mapping special keys to their display names.
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

    def draw_close_button(self):
        """
        Draws the close button on the Pygame window.
        """
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.button_rect)
        text_rect = self.button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(self.button_text, text_rect)

    def pygame_clear_screen(self):
        """
        Clears the screen at a set interval.
        """
        if self.running:
            self.current_text = []
            self.update_screen()
            self.timer = threading.Timer(CLEAR_DELAY, self.pygame_clear_screen)
            self.timer.start()

    def update_screen(self):
        """
        Updates the screen with the current text and the close button.
        """
        if self.running:
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_close_button()
            for i, line in enumerate(self.current_text):
                text = self.font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (10, 10 + i * self.font.get_height()))
            pygame.display.flip()

    def add_text(self, text):
        """
        Adds text to the screen and logs it if logging is enabled.
        """
        self.current_text.append(text)
        if len(self.current_text) * self.font.get_height() > self.screen_height:
            self.current_text.pop(0)
        self.update_screen()
        self.log_text(text)

    def log_text(self, text):
        """
        Logs text to the file if logging is enabled.
        """
        if self.enable_logging and self.logger:
            self.logger.info(text)

    def format_key_output(self):
        """
        Formats the output for key presses.
        """
        modifier_key_names = [keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.alt, keyboard.Key.alt_r, keyboard.Key.cmd, keyboard.Key.cmd_r]
        modifiers = [key for key in self.key_pressed if key in modifier_key_names]
        non_modifiers = [key for key in self.key_pressed if key not in modifier_key_names]

        formatted_keys = []
        for key in modifiers + non_modifiers:
            if key in self.special_keys:
                formatted_keys.append(self.special_keys[key].upper())
            elif hasattr(key, 'char') and key.char:
                formatted_keys.append(f"{key.char.upper()}")
            else:
                formatted_keys.append(str(key).upper())
        return ' + '.join(formatted_keys)

    def on_key_release(self, key):
        """
        Handles key release events.
        """
        if time.time() - self.last_key_press_time > MIN_KEY_PRESS_INTERVAL:
            self.key_pressed.clear()
        if key in self.key_pressed:
            self.key_pressed.remove(key)

    def on_key_press(self, key):
        """
        Handles key press events.
        """
        if time.time() - self.last_key_press_time > MIN_KEY_PRESS_INTERVAL:
            self.key_pressed.clear()
        self.key_pressed.add(key)
        formatted_output = self.format_key_output()
        self.add_text(formatted_output)
        self.last_key_press_time = time.time()

    def get_mouse_buttons(self):
        """
        Returns a dictionary mapping mouse buttons to their display names.
        """
        return {
            mouse.Button.left: 'Left Click'.upper(),
            mouse.Button.right: 'Right Click'.upper(),
            mouse.Button.middle: 'Middle Click'.upper()
        }

    def on_click(self, x, y, button, pressed):
        """
        Handles mouse click events.
        """
        if pressed:
            button_text = self.get_mouse_buttons().get(button, str(button))
            self.add_text(button_text)

    def on_scroll(self, x, y, dx, dy):
        """
        Handles mouse scroll events.
        """
        if dy > 0:
            self.add_text("Scroll Wheel Up".upper())
        elif dy < 0:
            self.add_text("Scroll Wheel Down".upper())

    def shutdown(self):
        """
        Shuts down the program, stopping listeners and closing resources.
        """
        self.running = False
        if self.timer:
            self.timer.cancel()
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        pygame.quit()
        if self.enable_logging and self.logger:
            logging.shutdown()

    def run(self):
        """
        Runs the main loop of the program.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.shutdown()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if self.button_rect.collidepoint(mouse_x, mouse_y):
                        self.shutdown()

if __name__ == "__main__":
    input_display = InputDisplay()
    input_display.run()
