# BOL Processing API - Troubleshooting Guide

## Common Issues and Solutions

### 1. "PDF file required" Error (400 Bad Request)

**Problem**: Getting error when uploading PDF file with 'pdf' key

**Possible Causes**:
- Request not sent as `multipart/form-data`
- File key name is not exactly 'pdf'
- Empty file or no file selected
- Using wrong HTTP method (should be POST)

**Solutions**:
1. **Check Content-Type**: Ensure request is `multipart/form-data`
2. **Verify Key Name**: File input field must be named exactly 'pdf'
3. **Select File**: Make sure a PDF file is actually selected
4. **Use POST Method**: The /process endpoint only accepts POST requests

**Thunder Client Setup**:
```
Method: POST
URL: http://localhost:5000/process
Body Type: form-data
Form Field: 
  - Name: pdf
  - Type: file
  - Value: [select your PDF file]
```

### 2. "Processing failed: CSV creation failed" Error (500)

**Problem**: PDF file is received but processing fails

**Possible Causes**:
- Missing dependencies (PyPDF2, pandas, etc.)
- PDF file is corrupted or unsupported format
- Missing parent directory processors
- Permissions issues with temp directories

**Solutions**:
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Check PDF File**: Try with a different, simple PDF file

3. **Verify Parent Directory**: Ensure the main processing files exist:
   - `../pdf_processor.py`
   - `../data_processor.py`
   - `../csv_exporter.py`

4. **Check Permissions**: Ensure write permissions for temp directories

### 3. File Upload Issues

**Problem**: File not being received by server

**Debugging Steps**:
1. **Enable Debug Mode**: The API already has debug logging enabled
2. **Check Server Logs**: Look for these debug messages:
   ```
   Content-Type: multipart/form-data; boundary=...
   Files in request: ['pdf']
   Form data: []
   Processing PDF: filename.pdf
   ```

3. **Verify File Format**: Only PDF files are accepted

### 4. Server Not Starting

**Problem**: Cannot connect to http://localhost:5000

**Solutions**:
1. **Start the Server**:
   ```bash
   cd pdf-csv-api
   python app.py
   ```

2. **Check Port**: Ensure port 5000 is available

3. **Firewall**: Check if firewall is blocking the port

## Testing the API

### Quick Test Script
Run the provided test script to verify all endpoints:
```bash
python test_api.py
```

### Manual Testing with curl
```bash
# Health check
curl http://localhost:5000/health

# Process PDF
curl -X POST -F "pdf=@your_file.pdf" http://localhost:5000/process --output result.csv
```

### Testing with Python requests
```python
import requests

# Test with PDF file
with open('your_file.pdf', 'rb') as f:
    files = {'pdf': ('test.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:5000/process', files=files)
    
print(f"Status: {response.status_code}")
if response.status_code == 200:
    with open('result.csv', 'wb') as f:
        f.write(response.content)
else:
    print(f"Error: {response.text}")
```

## Debug Mode

The API includes debug logging that shows:
- Request content type
- Files received in request
- Form data
- Processing status

Check the server console for these debug messages when troubleshooting.

## Common HTTP Status Codes

- **200 OK**: Success - CSV file returned
- **400 Bad Request**: Missing or invalid PDF file
- **500 Internal Server Error**: Processing failed

## Getting Help

1. **Check Server Logs**: Look at console output for error details
2. **Run Test Suite**: Use `python test_api.py` to verify setup
3. **Minimal Test**: Try with a simple, small PDF file first
4. **Check Dependencies**: Ensure all required packages are installed

## Dependencies

Make sure these are installed:
```bash
Flask==2.3.3
pandas==2.0.3
PyPDF2==3.0.1
requests==2.31.0
Werkzeug==2.3.7
```

## Thunder Client Common Issues

1. **Form Data**: Make sure Body Type is set to "form-data"
2. **File Selection**: Click on the file field and select your PDF
3. **Field Name**: Ensure the field name is exactly "pdf"
4. **Content Type**: Thunder Client should automatically set this to multipart/form-data 