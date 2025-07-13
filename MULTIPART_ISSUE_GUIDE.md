# Multipart Form Data Issue - Solution Guide

## 🔍 **Problem Diagnosed**

Your debug response shows:
```json
{
  "debug": {
    "content_type": "multipart/form-data",
    "expected_key": "pdf",
    "files_received": [],
    "form_data": []
  },
  "error": "PDF file required"
}
```

**Translation**: The request is being sent as multipart/form-data, but Flask isn't parsing any files or form data.

## 🎯 **Root Cause**

This typically happens when:
1. **Multipart boundary is malformed** - The boundary separator is missing or incorrect
2. **Content-Length header issues** - Missing or incorrect length
3. **Request body incomplete** - Data is cut off or corrupted
4. **Client-side encoding issues** - Thunder Client or client not properly encoding

## 🛠️ **Solutions (Try in Order)**

### 1. **Thunder Client Specific Fixes**

#### Option A: Reset Thunder Client Settings
1. In Thunder Client, click the **gear icon** (Settings)
2. Go to **Request Settings**
3. Ensure **Auto Headers** is enabled
4. Clear any manual Content-Type headers
5. Try the request again

#### Option B: Recreate the Request
1. Create a **new request** in Thunder Client
2. Set Method: **POST**
3. URL: `http://localhost:5000/process`
4. Body → Select **form-data**
5. Add field:
   - Key: `pdf`
   - Type: **File** (click dropdown)
   - Value: Click to select your PDF file
6. **Important**: Don't add any manual headers - let Thunder Client handle them

### 2. **Test with Debug Endpoint**

First, test the multipart parsing with our debug endpoint:

1. **URL**: `http://localhost:5000/debug/multipart`
2. **Method**: POST
3. **Body**: form-data with your PDF file
4. **Key**: `pdf`
5. **Type**: File

This will give you detailed debugging information.

### 3. **Alternative Testing Methods**

#### Option A: Use curl (Command Line)
```bash
curl -X POST -F "pdf=@your_file.pdf" http://localhost:5000/process
```

#### Option B: Use Python requests
```python
import requests

with open('your_file.pdf', 'rb') as f:
    files = {'pdf': f}
    response = requests.post('http://localhost:5000/process', files=files)
    print(response.status_code)
    print(response.text)
```

#### Option C: Use Postman
1. Create new POST request
2. URL: `http://localhost:5000/process`
3. Body → form-data
4. Key: `pdf`, Type: File
5. Select your PDF file

### 4. **Common Thunder Client Issues & Fixes**

#### Issue: File not being selected properly
- **Fix**: Make sure you **click the file field** and see the filename appear
- **Verify**: The field should show your filename, not be empty

#### Issue: Wrong content type
- **Fix**: Remove any manual `Content-Type` headers
- **Let Thunder Client auto-generate**: `multipart/form-data; boundary=...`

#### Issue: Large file problems
- **Fix**: Try with a **small PDF file** (< 1MB) first
- **Check**: File size limits in Thunder Client settings

### 5. **Flask Configuration Fix**

Add this to the Flask app configuration:

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
```

### 6. **Advanced Debugging**

If the above doesn't work, the enhanced debug endpoint will show:

```json
{
  "content_type": "multipart/form-data; boundary=...",
  "content_length": "actual_length",
  "has_raw_data": true,
  "raw_data_length": 1234,
  "parsing_issue": true,
  "suggestions": [...]
}
```

### 7. **Step-by-Step Thunder Client Setup**

1. **Open Thunder Client**
2. **Click "New Request"**
3. **Set Method**: POST
4. **Set URL**: `http://localhost:5000/process`
5. **Go to Body tab**
6. **Select "form-data"** (not raw, not json)
7. **Add Row**:
   - Key: `pdf`
   - Click dropdown → Select **"File"**
   - Click "Select File" → Choose your PDF
8. **Verify**: You should see your filename in the value field
9. **Send Request**

## 🚨 **If Nothing Works**

### Check Server Logs
When you send the request, check the server console for:
```
Request method: POST
Content-Type: multipart/form-data; boundary=...
Content-Length: 12345
Files in request: []
Form data: []
✗ WARNING: Multipart request but no files or form data parsed!
```

### Try Minimal Test
Create a simple HTML form to test:

```html
<!DOCTYPE html>
<html>
<body>
    <form action="http://localhost:5000/process" method="post" enctype="multipart/form-data">
        <input type="file" name="pdf" accept=".pdf">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
```

## 🎯 **Most Likely Solution**

Based on the symptoms, the most likely fix is:

1. **Recreate the Thunder Client request** from scratch
2. **Ensure Body type is "form-data"** (not raw)
3. **Key name is exactly "pdf"**
4. **Type is "File"** (not text)
5. **Actually select a PDF file**

## 📞 **Need More Help?**

If you're still having issues, provide:
1. Thunder Client version
2. Response from `/debug/multipart` endpoint
3. Server console logs
4. Screenshot of your Thunder Client request setup

The debug endpoint will give us the exact details needed to solve this! 