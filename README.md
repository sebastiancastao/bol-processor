# PDF-CSV BOL Processing API

External-use API service for processing Bill of Lading (BOL) PDF files and merging with CSV data. Three different architectural approaches provided for different use cases.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- poppler-utils (for PDF processing)

### Installation

```bash
# Clone/copy the pdf-csv-api directory
cd pdf-csv-api

# Install dependencies
pip install -r requirements.txt

# Install poppler (Linux/macOS)
sudo apt-get install poppler-utils  # Ubuntu/Debian
brew install poppler                 # macOS

# For Windows, download poppler and add to PATH
```

### Run API Server

Choose one of the three approaches:

```bash
# Approach 1: Minimal (Quick & Simple)
python approach1_minimal.py
# Server runs on http://localhost:8081

# Approach 2: Clean Architecture (Recommended)
python approach2_clean.py  
# Server runs on http://localhost:8082

# Approach 3: Production Microservice (High Scale)
python approach3_microservice.py
# Server runs on http://localhost:8083
```

## 📋 API Usage

### Approach 1 & 2: Synchronous Processing

**Process PDF with optional CSV:**
```bash
curl -X POST http://localhost:8082/process \
  -F "pdf=@your_bol_file.pdf" \
  -F "csv=@additional_data.csv" \
  -o result.csv
```

**Health Check:**
```bash
curl http://localhost:8082/health
```

### Approach 3: Asynchronous Processing

**Submit Job:**
```bash
curl -X POST http://localhost:8083/submit \
  -F "pdf=@your_bol_file.pdf" \
  -F "csv=@additional_data.csv" \
  -F "priority=high"
```

**Check Status:**
```bash
curl http://localhost:8083/status/{job_id}
```

**Download Result:**
```bash
curl http://localhost:8083/result/{job_id} -o result.csv
```

**System Metrics:**
```bash
curl http://localhost:8083/metrics
```

## 🏗️ Architecture Comparison

| Feature | Approach 1 | Approach 2 | Approach 3 |
|---------|------------|------------|------------|
| **Implementation Time** | 1-2 days | 3-5 days | 1-2 weeks |
| **Complexity** | Low | Medium | High |
| **Scalability** | Poor | Medium | Excellent |
| **Error Handling** | Basic | Robust | Comprehensive |
| **Monitoring** | None | Basic | Advanced |
| **Async Processing** | No | No | Yes |
| **Production Ready** | No | Yes | Yes |

## 🎯 Which Approach to Choose?

### **Approach 1: Minimal Refactoring**
- ✅ **Best for:** Prototypes, low-volume, quick implementation
- ✅ **Pros:** Simple, fast to implement, stateless
- ❌ **Cons:** Limited scalability, basic error handling

### **Approach 2: Clean Service Architecture** ⭐ **RECOMMENDED**
- ✅ **Best for:** Production apps, medium volume, maintainable code
- ✅ **Pros:** Clean design, robust errors, type safety, testable
- ❌ **Cons:** Synchronous only, more complex than Approach 1

### **Approach 3: Production Microservice**
- ✅ **Best for:** High-volume, enterprise, comprehensive monitoring
- ✅ **Pros:** Async processing, worker pools, metrics, scalable
- ❌ **Cons:** High complexity, resource intensive, long development

## 📊 Processing Pipeline

All approaches follow the same core processing pipeline:

```
1. PDF Upload → Extract text using pdfplumber
2. Text Processing → Parse invoices and table data  
3. CSV Generation → Create structured CSV from PDF data
4. CSV Merging → Merge with additional CSV data (optional)
5. Download → Return final processed CSV file
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# File size limits
MAX_FILE_SIZE_MB = 100

# Poppler configuration
POPPLER_PATH = None  # Auto-detect

# Logging
LOG_LEVEL = 'INFO'

# Production settings
PRODUCTION = False
```

## 📈 Performance Guidelines

### File Size Limits
- **PDF Files:** Up to 100MB
- **CSV Files:** Up to 50MB
- **Processing Time:** 30-120 seconds depending on file size

### Scalability
- **Approach 1:** 1-10 requests/hour
- **Approach 2:** 10-100 requests/hour  
- **Approach 3:** 100+ requests/hour

## 🧪 Testing

### Manual Testing
```bash
# Test with sample files
curl -X POST http://localhost:8082/process \
  -F "pdf=@sample_bol.pdf" \
  -o test_result.csv

# Verify result
head test_result.csv
```

### API Documentation
Each approach includes built-in API documentation:
```bash
curl http://localhost:8082/api/docs
```

## 🚀 Deployment

### Development
```bash
python approach2_clean.py
```

### Production (Approach 2)
```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 approach2_clean:app
```

### Production (Approach 3)
```bash
# With proper worker configuration
gunicorn -w 1 -b 0.0.0.0:8080 approach3_microservice:app
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim

# Install poppler
RUN apt-get update && apt-get install -y poppler-utils

# Copy and install
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Run desired approach
CMD ["python", "approach2_clean.py"]
```

## 🛠️ Development

### Adding Features

**Approach 1:** Modify `SimpleBOLProcessor` class
**Approach 2:** Add new services or enhance existing ones  
**Approach 3:** Add workers or enhance job processing

### Core Components

All approaches use these core processing components:
- **PDF Processing:** `pdfplumber` for text extraction
- **Data Processing:** Custom parsing for BOL table data
- **CSV Export:** `pandas` for CSV manipulation
- **File Handling:** Secure temporary file management

## 🐛 Troubleshooting

### Common Issues

**PDF Processing Fails:**
```bash
# Check poppler installation
pdfinfo --version

# Install poppler if missing
sudo apt-get install poppler-utils
```

**Memory Issues:**
```bash
# Reduce file size or use Approach 3 for better memory management
```

**Timeout Errors:**
```bash
# For large files, use Approach 3 async processing
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 API Response Examples

### Successful Processing (Approach 1 & 2)
```http
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename=bol_processed.csv

Invoice No.,Style,Cartons,Individual Pieces,...
A12345,STYLE001,10,100,...
```

### Job Submission (Approach 3)
```json
{
  "job_id": "uuid-here",
  "status": "queued", 
  "message": "Job submitted successfully",
  "status_url": "/status/uuid-here",
  "result_url": "/result/uuid-here"
}
```

### Error Response
```json
{
  "error": "PDF processing failed",
  "details": "Could not extract text from PDF"
}
```

## 🤝 Contributing

1. Choose the appropriate approach for your use case
2. Test thoroughly with real BOL files
3. Add comprehensive error handling
4. Document any new features

## 📄 License

MIT License - See original project for details

---

**Recommendation:** Start with **Approach 2** for most production use cases. It provides the best balance of reliability, maintainability, and implementation effort. 