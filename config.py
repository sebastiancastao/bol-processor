import os
import platform

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Poppler Configuration
POPPLER_PATH = os.getenv('POPPLER_PATH', '/usr/bin')

# File Processing
OUTPUT_CSV_NAME = "combined_data.csv"

# Models
OPENAI_MODEL = "o3-mini"

# UI Configuration
TYPING_DELAY = float(os.getenv('TYPING_DELAY', '0.02'))
LOADING_ANIMATION_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

# File Upload Configuration
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

# Processing Configuration
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')

# API Configuration
MAX_FILE_SIZE_MB = 100
MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Production Configuration
PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
DEBUG = not PRODUCTION 
