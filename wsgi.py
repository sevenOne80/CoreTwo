import sys
import os

# Add project to path
project_home = '/home/YOURUSERNAME/CoreTwo'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import create_app
application = create_app()
