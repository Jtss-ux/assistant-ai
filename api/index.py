import sys
import os

# Allow importing from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel's Python runtime expects the variable named 'app' or 'handler'
handler = app
