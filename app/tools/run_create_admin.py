from app.tools.create_admin import main
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


if __name__ == "__main__":
    main()
