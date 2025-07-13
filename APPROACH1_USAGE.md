# Approach 1 (Minimal Refactoring) API - Usage Guide

## Overview
This is the **minimal refactoring** approach that directly reuses your existing PDF processing components in a simple Flask API. It's perfect for quick deployment and testing.

## 🚀 Quick Start

### 1. Installation
```bash
cd pdf-csv-api
pip install -r requirements.txt
```

### 2. Configuration
The API uses the existing `config.py` file. Make sure your environment variables are set:

```bash
# Optional: Set OpenAI API key if you need AI features
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Set Poppler path on Windows
export POPPLER_PATH="C:/path/to/poppler/bin"
```

### 3. Start the API
```bash
python approach1_minimal.py
```

The API will start at `http://localhost:5000`

## 📋 API Endpoints

### Health Check
- **GET** `/health`
- Returns API status and configuration

```bash
curl http://localhost:5000/health
```

### Process PDF
- **POST** `/process`
- Main endpoint for PDF processing

**Example with file upload:**
```bash
curl -X POST -F "file=@your-document.pdf" http://localhost:5000/process
```

**Example with JSON data:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "test", "format": "json"}' \
  http://localhost:5000/process
```

### API Documentation
- **GET** `/api/docs`
- Returns complete API documentation

```bash
curl http://localhost:5000/api/docs
```

## 🧪 Testing

### Run the Test Suite
```bash
python test_approach1.py
```

### Manual Testing
1. Start the API server:
   ```bash
   python approach1_minimal.py
   ```

2. In another terminal, test the health check:
   ```bash
   curl http://localhost:5000/health
   ```

3. Test the process endpoint:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"message": "test"}' \
     http://localhost:5000/process
   ```

## 💡 Usage Examples

### Python Client Example
```python
import requests

# Health check
response = requests.get('http://localhost:5000/health')
print(response.json())

# Process a PDF file
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/process', files=files)
    print(response.json())
```

### JavaScript Client Example
```javascript
// Health check
fetch('http://localhost:5000/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Process data
fetch('http://localhost:5000/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'test processing',
    format: 'json'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `POPPLER_PATH`: Path to Poppler binaries (Windows only)
- `PORT`: API port (default: 5000)

### File Locations
- `config.py`: Configuration settings
- `approach1_minimal.py`: Main API server
- `core_processors.py`: Core processing logic
- `pdf_processor.py`: PDF processing component
- `data_processor.py`: Data processing component
- `csv_exporter.py`: CSV export component

## 🎯 Features

### ✅ What's Included
- **PDF Processing**: Extract text and data from PDF files
- **CSV Export**: Convert processed data to CSV format
- **Simple REST API**: Easy-to-use endpoints
- **Error Handling**: Comprehensive error responses
- **Health Monitoring**: Status and configuration endpoints
- **Documentation**: Built-in API documentation

### ⚠️ Limitations
- **No Session Management**: Stateless operation only
- **No File Persistence**: Files are processed in temporary directories
- **Basic Error Handling**: Simple error responses
- **No Authentication**: Open API (add authentication as needed)
- **Single Request**: One file per request

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Error: Address already in use
   ```
   Solution: Change the port in `approach1_minimal.py` or kill the existing process

2. **Import Errors**
   ```
   ImportError: No module named 'some_module'
   ```
   Solution: Install requirements: `pip install -r requirements.txt`

3. **Poppler Not Found**
   ```
   PopplerNotFoundError: Poppler not found
   ```
   Solution: Install Poppler or set `POPPLER_PATH` environment variable

4. **OpenAI API Key Missing**
   ```
   Warning: OpenAI API key not configured
   ```
   Solution: Set `OPENAI_API_KEY` environment variable (optional)

### Debug Mode
To run in debug mode with detailed logging:
```bash
python approach1_minimal.py --debug
```

## 🎨 Customization

### Adding New Endpoints
```python
@app.route('/custom-endpoint', methods=['POST'])
def custom_endpoint():
    try:
        # Your custom logic here
        return jsonify({"status": "success", "message": "Custom endpoint"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Modifying Response Format
```python
def create_response(success, message, data=None):
    response = {
        "success": success,
        "message": message,
        "timestamp": time.time()
    }
    if data:
        response["data"] = data
    return jsonify(response)
```

## 📈 Performance Tips

1. **File Size**: Keep PDF files under 16MB for optimal performance
2. **Memory**: API uses temporary directories and cleans up automatically
3. **Concurrency**: Single-threaded processing (add threading as needed)
4. **Caching**: No caching implemented (add Redis/Memcached as needed)

## 🔄 Migration Path

When ready to scale up:
1. **To Approach 2**: Add service architecture and better error handling
2. **To Approach 3**: Add async processing and job queues
3. **Production**: Add authentication, rate limiting, and monitoring

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test script (`test_approach1.py`) for examples
3. Examine the API documentation endpoint (`/api/docs`)

---

**Next Steps**: Once you're comfortable with Approach 1, consider upgrading to Approach 2 for better architecture and production readiness. 