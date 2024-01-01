import pygame
from pygame.locals import QUIT
from pynput import keyboard, mouse
import threading
import time
import os

class InputDisplay:
    def __init__(self, screen_width=300, screen_height=100, font_size=33, button_font_size=24):
        """Initialize the InputDisplay class with screen configuration and font settings."""
        # Environment and Screen Setup
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        self.clear_screen()

        # Screen Configuration
        self.screen_width, self.screen_height = screen_width, screen_height

        # Pygame Initialization
        pygame.init()
        self.font = pygame.font.Font(None, font_size)
        self.button_font = pygame.font.Font(None, button_font_size)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Screenkey")

        # Close Button Setup
        self.button_color = (200, 0, 0)  # Red
        self.button_width, self.button_height = 50, 15
        self.button_x, self.button_y = self.screen_width - self.button_width - 5, 5
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.button_text = self.button_font.render('X', True, (255, 255, 255))

        # Control Variables and Constants
        self.current_text = []
        self.clear_delay = 3600
        self.key_pressed = set()
        self.running = True
        self.timer = None
        self.last_key_press_time = 0
        self.min_key_press_interval = 0.5

        # Special Keys Mapping
        self.special_keys = self.get_special_keys()

        # Initialize Screen Clearing
        self.pygame_clear_screen()

        # Keyboard and Mouse Listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    @staticmethod
    def get_special_keys():
        """Return a dictionary mapping special keys to their descriptions."""
        # Special keys mapping
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
            keyboard.KeyCode.from_vk(65439): ','
            }

    @staticmethod
    def clear_screen():
        """Clear the console screen."""
        os_name = os.name
        os.system('cls' if os_name == 'nt' else 'clear')

    def draw_close_button(self):
        """Draw the close button on the screen."""
        pygame.draw.rect(self.screen, self.button_color, self.button_rect)
        text_rect = self.button_text.get_rect(center=(self.button_x + self.button_width / 2, self.button_y + self.button_height / 2))
        self.screen.blit(self.button_text, text_rect)

    def pygame_clear_screen(self):
        """Clear the Pygame screen after a delay."""
        if self.running:
            self.current_text = []
            self.update_screen()
            self.timer = threading.Timer(self.clear_delay, self.pygame_clear_screen)
            self.timer.start()

    def update_screen(self):
        """Update the screen with current text."""
        if self.running:
            self.screen.fill((0, 0, 0))
            self.draw_close_button()
            for i, line in enumerate(self.current_text):
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (10, 10 + i * self.font.get_height()))
            pygame.display.flip()

    def add_text(self, text):
        """Add text to the screen."""
        self.current_text.append(text)
        if len(self.current_text) * self.font.get_height() > self.screen_height:
            self.current_text.pop(0)
        self.update_screen()

    def format_key_output(self):
        """Format the output for keys pressed."""
        # Modifier keys
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
        """Handle key release events."""
        current_time = time.time()
        if current_time - self.last_key_press_time > self.min_key_press_interval:
            self.key_pressed.clear()
        if key in self.key_pressed:
            self.key_pressed.remove(key)

    def on_key_press(self, key):
        """Handle key press events."""
        current_time = time.time()
        if current_time - self.last_key_press_time > self.min_key_press_interval:
            self.key_pressed.clear()
        self.key_pressed.add(key)
        self.add_text(self.format_key_output())
        self.last_key_press_time = current_time

    @staticmethod
    def get_mouse_buttons():
        """Return a dictionary mapping mouse buttons to their descriptions."""
        return {
            mouse.Button.left: 'Left Click',
            mouse.Button.right: 'Right Click',
            mouse.Button.middle: 'Middle Click'
        }

    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if pressed:
            button_text = self.get_mouse_buttons().get(button, str(button))
            self.add_text(button_text.upper())

    def on_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        if dy > 0:
            self.add_text("Scroll Wheel Up".upper())
        elif dy < 0:
            self.add_text("Scroll Wheel Down".upper())

    def shutdown(self):
        """Shut down the application, releasing all resources."""
        self.running = False
        if self.timer:
            self.timer.cancel()
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        pygame.quit()

    def run(self):
        """Run the main application loop."""
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.shutdown()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if self.button_rect.collidepoint(mouse_x, mouse_y):
                            self.shutdown()
        except Exception as e:
            print(f"Error occurred: {e}")
            self.shutdown()

if __name__ == "__main__":
    input_display = InputDisplay()
    input_display.run()
