# Deployment Guide for BOL Processor

## Overview
This guide helps resolve common deployment issues, particularly the pandas and dependency problems you encountered.

## Files Created/Modified

### 1. `runtime.txt`
- Specifies Python 3.11.9 for better package compatibility
- Avoids Python 3.13 compilation issues with pandas

### 2. `requirements.txt` (Updated)
- Added missing dependencies: `pdfplumber`, `pdf2image`, `Pillow`, `openai`
- Updated pandas to `>=2.1.4` for Python 3.11 compatibility
- Updated Flask and Werkzeug to latest stable versions
- Added version constraints to prevent compatibility issues

### 3. `config.py` (Created)
- Contains environment variable defaults for deployment
- Handles missing config file in deployment environment

### 4. `test_dependencies.py` (Created)
- Test script to verify all dependencies work
- Run locally before deployment: `python test_dependencies.py`

## System Dependencies (for PDF processing)

Your deployment platform may need these system packages:

```bash
# For pdf2image (converts PDF to images)
apt-get update
apt-get install -y poppler-utils

# For general PDF processing
apt-get install -y libpoppler-dev

# For image processing (Pillow)
apt-get install -y libjpeg-dev libpng-dev libtiff-dev
```

## Environment Variables for Deployment

Set these in your deployment platform (Render, Heroku, etc.):

```bash
# Required for OpenAI functionality (if using AI features)
OPENAI_API_KEY=your_actual_api_key_here

# Optional configurations
POPPLER_PATH=/usr/bin
TYPING_DELAY=0.02
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
TEMP_DIR=/tmp
```

## Common Issues and Solutions

### 1. pandas compilation errors
**Fixed by**: Using Python 3.11.9 in `runtime.txt`

### 2. pdfplumber not found
**Fixed by**: Adding `pdfplumber>=0.9.0` to requirements.txt

### 3. pdf2image not found / version errors
**Fixed by**: Adding `pdf2image>=1.16.0,<2.0.0` and `Pillow>=9.0.0,<11.0.0` to requirements.txt
**Note**: pdf2image latest version is 1.17.0, not 3.x as initially specified

### 4. config.py not found
**Fixed by**: Creating config.py with environment variable defaults

### 5. OpenAI import errors
**Fixed by**: Adding `openai>=1.3.0` to requirements.txt

## Testing Before Deployment

1. **Local testing**:
   ```bash
   python test_dependencies.py
   python app.py
   ```

2. **Test the API**:
   ```bash
   curl http://localhost:5000/health
   ```

## Deployment Platform Specific Notes

### Render
- Uses `runtime.txt` for Python version
- Automatically installs system dependencies for common packages
- May need to add build command if poppler issues persist

### Heroku
- Uses `runtime.txt` for Python version
- May need buildpacks for PDF processing:
  ```bash
  heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
  ```

### Other Platforms
- Ensure Python 3.11 is available
- Install system dependencies for PDF processing
- Check if poppler-utils is available

## Next Steps

1. Deploy with the updated files
2. Check logs for any remaining dependency issues
3. Test the `/health` endpoint first
4. If issues persist, run the dependency test script in the deployment environment

## Troubleshooting Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test specific imports
python -c "import pdfplumber; print('pdfplumber works')"
python -c "import pdf2image; print('pdf2image works')"
python -c "import pandas; print('pandas works')"
``` 