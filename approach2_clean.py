#!/usr/bin/env python3
"""
Approach 2: Clean Service Architecture
======================================
Restructured for maintainability with proper service layers,
error handling, and separation of concerns.
"""

import os
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import core processors
import sys
sys.path.append('..')
from pdf_processor import PDFProcessor
from data_processor import DataProcessor
from csv_exporter import CSVExporter

class ProcessingStatus(Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingRequest:
    """Request model for BOL processing."""
    pdf_content: bytes
    pdf_filename: str
    csv_content: Optional[bytes] = None
    csv_filename: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the processing request."""
        if not self.pdf_content:
            raise ValueError("PDF content is required")
        if not self.pdf_filename.lower().endswith('.pdf'):
            raise ValueError("PDF file must have .pdf extension")
        if self.csv_content and self.csv_filename:
            valid_csv_extensions = ['.csv', '.xlsx', '.xls']
            if not any(self.csv_filename.lower().endswith(ext) for ext in valid_csv_extensions):
                raise ValueError("CSV file must have .csv, .xlsx, or .xls extension")

@dataclass 
class ProcessingResult:
    """Result model for BOL processing."""
    status: ProcessingStatus
    csv_content: Optional[bytes] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ValidationError(Exception):
    """Custom validation error."""
    pass

class ProcessingError(Exception):
    """Custom processing error."""
    pass

class FileService:
    """Service for file operations."""
    
    @staticmethod
    def save_temp_file(content: bytes, suffix: str) -> str:
        """Save content to temporary file and return path."""
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(content)
                return tmp.name
        except Exception as e:
            logger.error(f"Failed to save temporary file: {e}")
            raise ProcessingError(f"File save error: {str(e)}")
    
    @staticmethod
    def cleanup_files(*file_paths: str) -> None:
        """Clean up temporary files."""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {e}")

class PDFService:
    """Service for PDF processing operations."""
    
    def __init__(self):
        self.file_service = FileService()
    
    def process_pdf(self, pdf_content: bytes, working_dir: str) -> bool:
        """Process PDF and extract text."""
        try:
            # Save PDF to working directory
            pdf_path = os.path.join(working_dir, "input.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            
            # Process with PDF processor
            processor = PDFProcessor(working_dir)
            success = processor.process_first_pdf()
            
            if not success:
                raise ProcessingError("PDF text extraction failed")
            
            logger.info("PDF processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise ProcessingError(f"PDF processing error: {str(e)}")

class DataService:
    """Service for data processing operations."""
    
    def process_extracted_data(self, working_dir: str) -> bool:
        """Process extracted text data."""
        try:
            # Override session directory for existing processor
            processor = DataProcessor()
            processor.session_dir = working_dir
            processor.invoice_data = {}  # Reset data
            
            success = processor.process_all_files()
            
            if not success:
                raise ProcessingError("Data processing failed")
            
            logger.info("Data processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise ProcessingError(f"Data processing error: {str(e)}")

class CSVService:
    """Service for CSV operations."""
    
    def __init__(self):
        self.file_service = FileService()
    
    def create_initial_csv(self, working_dir: str) -> str:
        """Create initial CSV from processed data."""
        try:
            exporter = CSVExporter(working_dir)
            success = exporter.combine_to_csv()
            
            if not success:
                raise ProcessingError("CSV creation failed")
            
            csv_path = os.path.join(working_dir, "combined_data.csv")
            if not os.path.exists(csv_path):
                raise ProcessingError("CSV file not created")
            
            logger.info("Initial CSV created successfully")
            return csv_path
            
        except Exception as e:
            logger.error(f"CSV creation failed: {e}")
            raise ProcessingError(f"CSV creation error: {str(e)}")
    
    def merge_with_additional_csv(self, base_csv_path: str, additional_csv_content: bytes, 
                                additional_csv_filename: str) -> str:
        """Merge base CSV with additional CSV data."""
        try:
            # Save additional CSV to temp file
            additional_csv_path = self.file_service.save_temp_file(
                additional_csv_content, 
                os.path.splitext(additional_csv_filename)[1]
            )
            
            try:
                # Read both CSVs
                base_df = pd.read_csv(base_csv_path, dtype=str)
                
                # Handle different file types
                if additional_csv_filename.lower().endswith('.csv'):
                    additional_df = pd.read_csv(additional_csv_path, dtype=str)
                else:
                    additional_df = pd.read_excel(additional_csv_path, dtype=str)
                
                # TODO: Implement sophisticated merge logic from original process_csv_file
                # For now, simple concatenation
                merged_df = pd.concat([base_df, additional_df], ignore_index=True)
                
                # Save merged result
                merged_df.to_csv(base_csv_path, index=False)
                
                logger.info(f"CSV merge completed: {len(base_df)} + {len(additional_df)} rows")
                return base_csv_path
                
            finally:
                self.file_service.cleanup_files(additional_csv_path)
                
        except Exception as e:
            logger.error(f"CSV merge failed: {e}")
            raise ProcessingError(f"CSV merge error: {str(e)}")

class BOLProcessingService:
    """Main service for BOL processing orchestration."""
    
    def __init__(self):
        self.pdf_service = PDFService()
        self.data_service = DataService()
        self.csv_service = CSVService()
        self.file_service = FileService()
    
    def process(self, request: ProcessingRequest) -> ProcessingResult:
        """Process BOL request and return result."""
        working_dir = None
        
        try:
            # Validate request
            request.validate()
            
            # Create working directory
            working_dir = tempfile.mkdtemp(prefix="bol_api_")
            logger.info(f"Processing started in: {working_dir}")
            
            # Step 1: Process PDF
            logger.info("Step 1: Processing PDF")
            self.pdf_service.process_pdf(request.pdf_content, working_dir)
            
            # Step 2: Process extracted data
            logger.info("Step 2: Processing extracted data")
            self.data_service.process_extracted_data(working_dir)
            
            # Step 3: Create initial CSV
            logger.info("Step 3: Creating initial CSV")
            csv_path = self.csv_service.create_initial_csv(working_dir)
            
            # Step 4: Merge with additional CSV if provided
            if request.csv_content and request.csv_filename:
                logger.info("Step 4: Merging with additional CSV")
                csv_path = self.csv_service.merge_with_additional_csv(
                    csv_path, request.csv_content, request.csv_filename
                )
            
            # Step 5: Read final result
            with open(csv_path, 'rb') as f:
                csv_content = f.read()
            
            logger.info("Processing completed successfully")
            
            return ProcessingResult(
                status=ProcessingStatus.COMPLETED,
                csv_content=csv_content,
                metadata={
                    'pdf_filename': request.pdf_filename,
                    'csv_filename': request.csv_filename,
                    'output_size': len(csv_content)
                }
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return ProcessingResult(
                status=ProcessingStatus.FAILED,
                error_message=f"Validation error: {str(e)}"
            )
            
        except ProcessingError as e:
            logger.error(f"Processing error: {e}")
            return ProcessingResult(
                status=ProcessingStatus.FAILED,
                error_message=f"Processing error: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ProcessingResult(
                status=ProcessingStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}"
            )
            
        finally:
            # Cleanup working directory
            if working_dir and os.path.exists(working_dir):
                try:
                    shutil.rmtree(working_dir)
                    logger.debug(f"Cleaned up working directory: {working_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup working directory: {e}")

# Flask Application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Initialize service
bol_service = BOLProcessingService()

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(Exception)
def handle_general_error(e):
    logger.error(f"Unhandled error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Enhanced health check."""
    return jsonify({
        'status': 'healthy',
        'service': 'BOL Processing API',
        'approach': 'clean_architecture',
        'version': '2.0',
        'features': [
            'Service layer separation',
            'Comprehensive error handling', 
            'Request/response validation',
            'Structured logging',
            'Proper cleanup'
        ]
    })

@app.route('/process', methods=['POST'])
def process_bol():
    """Main processing endpoint with enhanced error handling."""
    
    try:
        # Validate request structure
        if 'pdf' not in request.files:
            return jsonify({'error': 'PDF file required in form data'}), 400
        
        pdf_file = request.files['pdf']
        csv_file = request.files.get('csv')
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No PDF file selected'}), 400
        
        # Create processing request
        processing_request = ProcessingRequest(
            pdf_content=pdf_file.read(),
            pdf_filename=secure_filename(pdf_file.filename),
            csv_content=csv_file.read() if csv_file and csv_file.filename != '' else None,
            csv_filename=secure_filename(csv_file.filename) if csv_file and csv_file.filename != '' else None
        )
        
        # Process request
        result = bol_service.process(processing_request)
        
        # Handle result
        if result.status == ProcessingStatus.COMPLETED:
            # Return CSV as download
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
                tmp.write(result.csv_content)
                tmp.flush()
                
                return send_file(
                    tmp.name,
                    as_attachment=True,
                    download_name='bol_processed.csv',
                    mimetype='text/csv'
                )
        else:
            # Return error
            return jsonify({
                'error': result.error_message,
                'status': result.status.value
            }), 400
        
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return jsonify({'error': 'Request processing failed'}), 500

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Comprehensive API documentation."""
    return jsonify({
        'service': 'BOL Processing API - Clean Architecture',
        'version': '2.0',
        'endpoints': {
            'POST /process': {
                'description': 'Process PDF and optional CSV files',
                'parameters': {
                    'pdf': 'PDF file (required, multipart/form-data, max 100MB)',
                    'csv': 'CSV/Excel file (optional, multipart/form-data)'
                },
                'response': 'Processed CSV file download or error details',
                'status_codes': {
                    '200': 'Success - CSV file download',
                    '400': 'Bad request - validation or processing error',
                    '413': 'File too large',
                    '500': 'Internal server error'
                }
            },
            'GET /health': {
                'description': 'Service health check',
                'response': 'Service status and capabilities'
            }
        },
        'architecture': {
            'services': [
                'FileService - File operations and cleanup',
                'PDFService - PDF processing and text extraction',
                'DataService - Data processing and invoice handling',
                'CSVService - CSV creation and merging',
                'BOLProcessingService - Main orchestration'
            ],
            'features': [
                'Service layer separation',
                'Comprehensive error handling',
                'Request/response validation',
                'Structured logging',
                'Proper resource cleanup',
                'Type hints and documentation'
            ]
        },
        'advantages': [
            'Clean separation of concerns',
            'Robust error handling',
            'Easy to test and maintain',
            'Comprehensive logging',
            'Type safety',
            'Proper resource management'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True) 