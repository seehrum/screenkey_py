Screenkey User Manual
Introduction

Screenkey is a lightweight application that displays keyboard and mouse actions on your screen, making it an excellent tool for presentations, screencasts, or educational purposes. This manual will guide you through using Screenkey, from installation to daily use.
Version:

3.3
Installation

Prerequisites: Python (version 3.x) and the pynput library.

    Install Python: Download and install Python from python.org.
    Install pynput: Open your terminal or command prompt and run pip install pynput.
    Download Screenkey: Obtain the Screenkey script from its source or download location.

Starting the Application

To start Screenkey, navigate to the folder containing the script and run python screenkey.py in your terminal or command prompt.
Features and Configuration
Display Window

    Position: Default at (300, 300) on your screen.
    Size: 300x100 pixels.
    Always on Top: The display window stays above other windows.
    Customization: Text color, background color, and font settings (size, bold, type) are customizable through the CONFIG dictionary in the script.

Keyboard and Mouse Display

    Real-time Display: Shows pressed keys and mouse actions.
    Uppercase Option: Converts all displayed text to uppercase.
    Special Key Support: Special keys (like Ctrl, Alt) are displayed with their names.

Logging

    Enable Logging: Set to True by default. Records all key and mouse actions to a file named key_log.txt.
    Log Format: Timestamped entries for easy tracking.

Usage

Once the application is running, it will display a small window on your screen. As you use your keyboard and mouse, the actions will appear in this window. This is particularly useful for demonstrating software or teaching.
Keyboard Interaction

    Special Keys: When pressed, keys like Shift, Ctrl, Alt are displayed.
    Key Combinations: Simultaneous key presses are shown combined (e.g., Ctrl+C).

Mouse Interaction

    Clicks and Scrolls: Displays left, right, and middle mouse clicks, as well as scroll actions.

Exiting the Application

To close Screenkey, simply close the window or use the standard window closing mechanisms of your operating system.
Troubleshooting and Support

If you encounter any issues or have questions, refer to the following resources:

    Error Logs: Check key_log.txt for error messages.
    Python Documentation: For issues related to Python or its libraries.
    Online Communities: Python and programming forums can be valuable resources for troubleshooting.
