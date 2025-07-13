#!/usr/bin/env python3
"""
Approach 1: Minimal Refactoring API
=====================================
Extract core processing logic with minimal changes.
Focus on simplicity and speed of implementation.
"""

import os
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import flask

# Import existing processors (with minimal modifications)
import sys
sys.path.append('..')
from pdf_processor import PDFProcessor
from data_processor import DataProcessor  
from csv_exporter import CSVExporter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

class SimpleBOLProcessor:
    """Simplified BOL processor for API-only use."""
    
    @staticmethod
    def process_pdf_to_csv(pdf_file_path, csv_file_path=None):
        """Process PDF and optional CSV, return final CSV path."""
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Copy PDF to temp directory
                pdf_name = os.path.basename(pdf_file_path)
                temp_pdf_path = os.path.join(temp_dir, pdf_name)
                shutil.copy2(pdf_file_path, temp_pdf_path)
                
                # Step 1: Process PDF
                pdf_processor = PDFProcessor(temp_dir)
                if not pdf_processor.process_first_pdf():
                    raise Exception("PDF processing failed")
                
                # Step 2: Process extracted text
                data_processor = DataProcessor()
                data_processor.session_dir = temp_dir  # Override session dir
                if not data_processor.process_all_files():
                    raise Exception("Text processing failed")
                
                # Step 3: Create initial CSV
                csv_exporter = CSVExporter(temp_dir)
                if not csv_exporter.combine_to_csv():
                    raise Exception("CSV creation failed")
                
                # Step 4: Merge with additional CSV if provided
                final_csv_path = os.path.join(temp_dir, "combined_data.csv")
                
                if csv_file_path and os.path.exists(csv_file_path):
                    # Simple CSV merge logic (simplified from original)
                    pdf_df = pd.read_csv(final_csv_path, dtype=str)
                    csv_df = pd.read_csv(csv_file_path, dtype=str)
                    
                    # Basic merge - in production, would implement full logic
                    merged_df = pd.concat([pdf_df, csv_df], ignore_index=True)
                    merged_df.to_csv(final_csv_path, index=False)
                
                # Return the final CSV content
                with open(final_csv_path, 'rb') as f:
                    return f.read()
                    
            except Exception as e:
                raise Exception(f"Processing failed: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    """API root endpoint with welcome message and available endpoints."""
    return jsonify({
        'message': 'BOL Processing API - Approach 1 (Minimal Refactoring)',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'process': '/process (POST)',
            'documentation': '/api/docs'
        },
        'usage': {
            'health_check': 'GET /health',
            'process_pdf': 'POST /process with file upload',
            'get_docs': 'GET /api/docs'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Simple health check."""
    return jsonify({
        'status': 'healthy',
        'service': 'BOL Processing API',
        'approach': 'minimal'
    })

@app.route('/process', methods=['POST'])
def process_bol():
    """Main processing endpoint - accepts PDF and optional CSV."""
    
    try:
        # Enhanced debugging
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Content-Length: {request.headers.get('Content-Length', 'Not set')}")
        print(f"Files in request: {list(request.files.keys())}")
        print(f"Form data: {list(request.form.keys())}")
        print(f"Raw request headers: {dict(request.headers)}")
        
        # Check if request has any data at all
        if hasattr(request, 'data') and request.data:
            print(f"Raw data length: {len(request.data)}")
            print(f"Raw data preview: {request.data[:200]}")
        
        # Check if Flask is parsing multipart correctly
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            print("✓ Multipart request detected")
            if not request.files and not request.form:
                print("✗ WARNING: Multipart request but no files or form data parsed!")
                print("This might indicate a parsing issue with the multipart data.")
        
        # Validate request
        if 'pdf' not in request.files:
            return jsonify({
                'error': 'PDF file required',
                'debug': {
                    'content_type': request.content_type,
                    'content_length': request.headers.get('Content-Length', 'Not set'),
                    'files_received': list(request.files.keys()),
                    'form_data': list(request.form.keys()),
                    'expected_key': 'pdf',
                    'has_raw_data': bool(hasattr(request, 'data') and request.data),
                    'raw_data_length': len(request.data) if hasattr(request, 'data') and request.data else 0
                }
            }), 400
        
        pdf_file = request.files['pdf']
        csv_file = request.files.get('csv')
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No PDF file selected'}), 400
        
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        print(f"Processing PDF: {pdf_file.filename}")
        
        # Save uploaded files to temporary locations
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            pdf_file.save(tmp_pdf.name)
            pdf_path = tmp_pdf.name
        
        csv_path = None
        if csv_file and csv_file.filename != '':
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_csv:
                csv_file.save(tmp_csv.name)
                csv_path = tmp_csv.name
        
        try:
            # Process files
            result_csv = SimpleBOLProcessor.process_pdf_to_csv(pdf_path, csv_path)
            
            # Clean up temp files
            os.unlink(pdf_path)
            if csv_path:
                os.unlink(csv_path)
            
            # Return CSV as download
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_result:
                tmp_result.write(result_csv)
                tmp_result.flush()
                
                return send_file(
                    tmp_result.name,
                    as_attachment=True,
                    download_name='bol_processed.csv',
                    mimetype='text/csv'
                )
                
        except Exception as e:
            # Clean up temp files on error
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            if csv_path and os.path.exists(csv_path):
                os.unlink(csv_path)
            raise e
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/multipart', methods=['POST'])
def debug_multipart():
    """Debug endpoint to test multipart form data parsing."""
    
    debug_info = {
        'request_method': request.method,
        'content_type': request.content_type,
        'content_length': request.headers.get('Content-Length', 'Not set'),
        'files_received': list(request.files.keys()),
        'form_data': list(request.form.keys()),
        'has_raw_data': bool(hasattr(request, 'data') and request.data),
        'raw_data_length': len(request.data) if hasattr(request, 'data') and request.data else 0,
        'headers': dict(request.headers),
        'flask_version': flask.__version__
    }
    
    # Try to parse files manually if Flask isn't parsing them
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        debug_info['multipart_detected'] = True
        
        if not request.files and not request.form:
            debug_info['parsing_issue'] = True
            debug_info['suggestions'] = [
                'Check if Content-Length header is set correctly',
                'Verify multipart boundary is properly formatted',
                'Ensure file data is not corrupted',
                'Try with a smaller file',
                'Check if request body is complete'
            ]
    
    # Log debug info
    print("=== MULTIPART DEBUG INFO ===")
    for key, value in debug_info.items():
        print(f"{key}: {value}")
    print("===========================")
    
    return jsonify(debug_info)

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation."""
    return jsonify({
        'service': 'BOL Processing API - Minimal Approach',
        'endpoints': {
            'POST /process': {
                'description': 'Process PDF and optional CSV files',
                'parameters': {
                    'pdf': 'PDF file (required, multipart/form-data)',
                    'csv': 'CSV file (optional, multipart/form-data)'
                },
                'response': 'Processed CSV file download'
            },
            'GET /health': {
                'description': 'Health check',
                'response': 'Service status'
            },
            'POST /debug/multipart': {
                'description': 'Debug multipart form data parsing',
                'response': 'Debug information about the request'
            }
        },
        'advantages': [
            'Simple and fast to implement',
            'Uses existing processing logic',
            'Stateless operation',
            'Minimal dependencies'
        ],
        'limitations': [
            'No session management',
            'Limited error handling',
            'Basic CSV merge logic',
            'No async processing'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 