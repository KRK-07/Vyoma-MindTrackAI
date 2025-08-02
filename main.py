import signal
import sys
import atexit
from auth import login_with_google
from gui import launch_gui
from keylogger import start_keylogger
from analyzer import reset_alert_status

def cleanup():
    """Reset alert status when app exits or crashes"""
    reset_alert_status()

def signal_handler(signum, frame):
    """Handle Ctrl+C and other signals"""
    print(f"\nReceived signal {signum}. Cleaning up...")
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Register cleanup functions for various exit scenarios
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request
    
    try:
        user = login_with_google()
        listener = start_keylogger()
        launch_gui(user)
        listener.stop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        cleanup()
    except Exception as e:
        print(f"Application crashed with error: {e}")
        cleanup()
        raise
    finally:
        cleanup()
