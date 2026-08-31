import os
import sys

# Get the backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure the backend directory is available on Python's import path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Tell Django which settings module to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Vercel can use either `app` or `application`
app = application