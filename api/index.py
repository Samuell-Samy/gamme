from django.core.wsgi import get_wsgi_application
import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Thunder_Games.settings')

# Get the WSGI application
application = get_wsgi_application()

# Vercel expects the handler to be named 'app'
app = application
