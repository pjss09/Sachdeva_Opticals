import os
import sys
import logging

# Setup logging to log into a file for debugging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

logging.debug("Starting the application")

# Check if we are running inside a PyInstaller bundle
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

logging.debug(f"Base path: {base_path}")

# Check if manage.py exists
manage_path = os.path.join(base_path, 'manage.py')

if os.path.exists(manage_path):
    logging.debug(f"manage.py found at {manage_path}")
    # Try to run Django server here
    os.system("start cmd /k python manage.py runserver")
else:
    logging.debug("manage.py not found")
    print("manage.py not found")

logging.debug("Application ended")
