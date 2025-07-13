# Thunder Client Guide for BOL Processing API

## 🚀 How to Test `/process` Endpoint with Thunder Client

Thunder Client is a REST API client for VS Code. Here's how to set up and test your BOL Processing API.

---

## 📋 **Setup Thunder Client**

1. **Install Thunder Client**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Thunder Client"
   - Install by Ranga Vadhineni

2. **Open Thunder Client**:
   - Click the Thunder Client icon in the sidebar
   - Or use Ctrl+Shift+P → "Thunder Client: Open"

---

## 🔧 **Test 1: Health Check**

First, verify your server is running:

### Request Setup:
- **Method**: `GET`
- **URL**: `http://localhost:5000/health`
- **Headers**: None needed
- **Body**: None

### Expected Response:
```json
{
  "status": "healthy",
  "service": "BOL Processing API",
  "approach": "minimal"
}
```

---

## 📄 **Test 2: Process PDF Only**

### Request Setup:
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`

### Headers:
```
Content-Type: multipart/form-data
```
*Note: Thunder Client automatically sets this when you use Form data*

### Body (Form Data):
1. Click **"Body"** tab
2. Select **"Form"** (not "Form Encoded")
3. Add field:
   - **Key**: `pdf`
   - **Type**: `File` (click the dropdown)
   - **Value**: Browse and select your PDF file

### Visual Guide:
```
Body Tab:
┌─────────────────────────────────────┐
│ ○ None  ○ Form  ○ Form Encoded     │
│ ○ JSON  ○ XML   ○ Raw              │
└─────────────────────────────────────┘

Form Data:
┌─────────┬──────┬─────────────────────┐
│   Key   │ Type │        Value        │
├─────────┼──────┼─────────────────────┤
│   pdf   │ File │ [Browse for file]   │
└─────────┴──────┴─────────────────────┘
```

### Expected Response:
- **Status**: `200 OK`
- **Content-Type**: `application/octet-stream` or `text/csv`
- **Body**: CSV file content (will be downloaded)

---

## 📊 **Test 3: Process PDF + CSV**

### Request Setup:
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`

### Body (Form Data):
1. Click **"Body"** tab
2. Select **"Form"**
3. Add two fields:

#### Field 1:
- **Key**: `pdf`
- **Type**: `File`
- **Value**: Browse and select your PDF file

#### Field 2:
- **Key**: `csv`
- **Type**: `File`
- **Value**: Browse and select your CSV file

### Visual Guide:
```
Form Data:
┌─────────┬──────┬─────────────────────┐
│   Key   │ Type │        Value        │
├─────────┼──────┼─────────────────────┤
│   pdf   │ File │ [Your PDF file]     │
│   csv   │ File │ [Your CSV file]     │
└─────────┴──────┴─────────────────────┘
```

---

## ❌ **Test 4: Error Cases**

### Test 4a: Missing PDF
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`
- **Body**: Empty or no `pdf` field
- **Expected**: `400 Bad Request` with error message

### Test 4b: Wrong Field Name
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`
- **Body Form Data**:
  - **Key**: `wrong_field` (instead of `pdf`)
  - **Type**: `File`
  - **Value**: Any file
- **Expected**: `400 Bad Request`

---

## 📥 **Handling Responses**

### Success Response (200):
- The response will be a CSV file
- Thunder Client will show the raw CSV content
- You can save it by clicking the **"Save Response"** button

### Error Response (400/500):
```json
{
  "error": "PDF file required"
}
```

---

## 🛠️ **Thunder Client Collection Setup**

Create a collection for easy testing:

### 1. Create New Collection:
- Click **"Collections"** in Thunder Client
- Click **"New Collection"**
- Name: `BOL Processing API`

### 2. Add Requests to Collection:

#### Request 1: Health Check
- **Name**: `Health Check`
- **Method**: `GET`
- **URL**: `http://localhost:5000/health`

#### Request 2: API Docs
- **Name**: `API Documentation`
- **Method**: `GET`
- **URL**: `http://localhost:5000/api/docs`

#### Request 3: Process PDF
- **Name**: `Process PDF Only`
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`
- **Body**: Form data with `pdf` file field

#### Request 4: Process PDF + CSV
- **Name**: `Process PDF + CSV`
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`
- **Body**: Form data with `pdf` and `csv` file fields

#### Request 5: Error Test
- **Name**: `Test Missing PDF Error`
- **Method**: `POST`
- **URL**: `http://localhost:5000/process`
- **Body**: Empty

---

## 🎯 **Quick Testing Steps**

1. **Start your server**:
   ```bash
   cd pdf-csv-api
   python app.py
   ```

2. **Test in this order**:
   1. Health Check → Should return 200
   2. API Docs → Should return 200 with documentation
   3. Error Test → Should return 400
   4. Process PDF → Should return 200 with CSV file (if you have a PDF)

---

## 📝 **Sample Test Data**

If you need test files:

### Create a test CSV file:
```csv
Invoice No.,Style,Cartons,Individual Pieces,Invoice Date,Ship-to Name,Order No.,Delivery Date,Cancel Date
INV001,STYLE001,5,100,01/15/2025,Test Company,ORD001,02/01/2025,3152025
INV002,STYLE002,3,60,01/16/2025,Burlington Store,ORD002,02/05/2025,2202025
```

### For PDF testing:
- Use any PDF file initially to test the upload mechanism
- For real processing, use actual BOL PDF files

---

## 🔍 **Troubleshooting**

### Common Issues:

1. **Connection Refused**:
   - Make sure server is running: `python app.py`
   - Check URL: `http://localhost:5000`

2. **File Upload Not Working**:
   - Ensure you select **"Form"** not **"Form Encoded"**
   - Make sure field type is set to **"File"**

3. **400 Bad Request**:
   - Check that field name is exactly `pdf`
   - Ensure file is actually selected

4. **500 Internal Server Error**:
   - Check server console for detailed error messages
   - Verify PDF file is valid

---

## 💡 **Pro Tips**

1. **Save Responses**: Click "Save Response" to download CSV files
2. **Environment Variables**: Use Thunder Client environments for different servers
3. **Test Scripts**: Use Thunder Client's test scripts for automated validation
4. **History**: Thunder Client saves request history for easy re-testing

---

**Happy Testing! 🚀** 