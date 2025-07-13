#!/usr/bin/env python3
"""
Core Processing Classes for API-Only BOL Processing
===================================================
Simplified, self-contained versions of the processing logic
optimized for API use without complex dependencies.
"""

import os
import re
import csv
import gc
import glob
import tempfile
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import pdfplumber

class SimplePDFProcessor:
    """Simplified PDF processor for API use."""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
    
    def process_pdf(self, pdf_path: str) -> bool:
        """Extract text from PDF and save as numbered TXT files."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    raise Exception("PDF has no pages")
                
                page_count = len(pdf.pages)
                print(f"📄 Processing {page_count} pages")
                
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        
                        if not text or text.strip() == "":
                            text = f"[Page {i+1} - No text content found]"
                        
                        text_path = os.path.join(self.working_dir, f"{i+1}.txt")
                        with open(text_path, 'w', encoding='utf-8') as text_file:
                            text_file.write(text)
                        
                        print(f"✅ Saved text from page {i+1}")
                        
                        # Memory management
                        if hasattr(page, 'flush_cache'):
                            page.flush_cache()
                        
                        if i % 5 == 0:
                            gc.collect()
                            
                    except Exception as page_error:
                        print(f"⚠️ Error processing page {i+1}: {str(page_error)}")
                        continue
            
            print(f"✅ Text extraction completed for {page_count} pages")
            return True
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return False

class SimpleDataProcessor:
    """Simplified data processor for API use."""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.invoice_data = {}
    
    def process_all_files(self) -> bool:
        """Process all TXT files in the working directory."""
        try:
            txt_files = [f for f in os.listdir(self.working_dir) if f.endswith('.txt')]
            if not txt_files:
                print("No TXT files found")
                return False
            
            print(f"Found {len(txt_files)} TXT files to process")
            
            # Phase 1: Collect data from all files
            for txt_file in txt_files:
                self._collect_invoice_data(txt_file)
            
            # Phase 2: Process collected data
            for invoice_no, data in self.invoice_data.items():
                self._process_invoice_data(invoice_no, data)
            
            # Phase 3: Cleanup TXT files
            for txt_file in txt_files:
                file_path = os.path.join(self.working_dir, txt_file)
                try:
                    os.remove(file_path)
                    print(f"Cleaned up {txt_file}")
                except Exception as e:
                    print(f"Warning: Could not remove {txt_file}: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"Error processing files: {str(e)}")
            return False
    
    def _collect_invoice_data(self, txt_file: str):
        """Collect data from a single TXT file."""
        file_path = os.path.join(self.working_dir, txt_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            invoice_no = self._get_invoice_no(content)
            if not invoice_no:
                print(f"Invoice number not found in {txt_file}")
                return
            
            # Initialize invoice data if not exists
            if invoice_no not in self.invoice_data:
                self.invoice_data[invoice_no] = {
                    'pages': [],
                    'has_totals': False
                }
            
            # Extract table data
            table_data = self._extract_table_data(content)
            bol_cube = self._extract_bol_cube(content)
            
            page_data = {
                'rows': table_data['rows'],
                'has_totals': table_data['has_totals'],
                'totals': table_data['totals'],
                'bol_cube': bol_cube
            }
            
            self.invoice_data[invoice_no]['pages'].append(page_data)
            
            if table_data['has_totals']:
                self.invoice_data[invoice_no]['has_totals'] = True
            
            print(f"Collected data from {txt_file}: {len(table_data['rows'])} rows")
            
        except Exception as e:
            print(f"Error collecting data from {txt_file}: {str(e)}")
    
    def _extract_table_data(self, content: str) -> Dict[str, Any]:
        """Extract table data from content."""
        lines = content.splitlines()
        rows = []
        totals = {'pieces': '', 'weight': ''}
        has_totals = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for totals
            if "TOTAL CARTONS" in line.upper():
                has_totals = True
                # Extract totals from this line or subsequent lines
                numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', line)
                if len(numbers) >= 2:
                    totals['pieces'] = numbers[-2].replace(',', '')
                    totals['weight'] = numbers[-1].replace(',', '')
            
            # Check for table rows
            if self._is_valid_table_row(line_stripped):
                row_data = self._parse_table_row(line_stripped)
                if row_data:
                    rows.append(row_data)
        
        return {
            'rows': rows,
            'has_totals': has_totals,
            'totals': totals
        }
    
    def _is_valid_table_row(self, line: str) -> bool:
        """Check if line is a valid table row."""
        if not line or len(line) < 10:
            return False
        
        # Look for patterns that indicate this is a data row
        if re.match(r'^\d+', line):
            return True
        
        # Contains multiple numeric values
        numbers = re.findall(r'\d+', line)
        if len(numbers) >= 3:
            return True
        
        # Contains style patterns
        if re.search(r'\b[A-Z]+\d+\b', line) or re.search(r'\b\d+[A-Z]+\b', line):
            tokens = line.split()
            if len(tokens) >= 3 and any(re.match(r'^\d+', token) for token in tokens):
                return True
        
        return False
    
    def _parse_table_row(self, line: str) -> Optional[List[str]]:
        """Parse a table row into components."""
        try:
            # Simple splitting - can be enhanced based on specific format
            tokens = line.split()
            if len(tokens) >= 3:
                return tokens
        except Exception:
            pass
        return None
    
    def _extract_bol_cube(self, content: str) -> str:
        """Extract BOL Cube from content."""
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "SHIPPING INSTRUCTIONS:" in line.upper():
                j = i - 1
                while j >= 0:
                    candidate = lines[j].strip()
                    match = re.search(r'\b\d{1,3}\.\d{2}\b', candidate)
                    if match:
                        return match.group(0)
                    j -= 1
                break
        return ""
    
    def _get_invoice_no(self, content: str) -> str:
        """Extract invoice number from content."""
        lines = content.splitlines()
        for line in lines[:10]:
            if "BILL OF LADING" in line.upper():
                match = re.search(r'BILL OF LADING\s+([A-Z]\d+)', line, re.IGNORECASE)
                if match:
                    return match.group(1)
        return ""
    
    def _process_invoice_data(self, invoice_no: str, data: Dict[str, Any]):
        """Process collected invoice data and create CSV."""
        print(f"Processing Invoice {invoice_no}")
        
        # Collect all rows from all pages
        all_rows = []
        bol_cube = ""
        
        for page in data['pages']:
            all_rows.extend(page['rows'])
            if page['bol_cube']:
                bol_cube = page['bol_cube']
        
        if not all_rows:
            print(f"No rows found for invoice {invoice_no}")
            return
        
        # Create CSV for this invoice
        csv_path = os.path.join(self.working_dir, f"{invoice_no}.csv")
        
        # Simple CSV creation - can be enhanced with proper column mapping
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            header = [
                "Invoice No.", "Style", "Cartons", "Individual Pieces", 
                "BOL Cube", "Ship To Name", "Order Date", "Purchase Order No.",
                "Start Date", "Cancel Date", "Pallet", "Burlington Cube", "Final Cube"
            ]
            writer.writerow(header)
            
            # Write data rows (simplified mapping)
            for row in all_rows:
                if isinstance(row, list) and len(row) >= 3:
                    csv_row = [invoice_no] + row[:12]  # Take first 12 columns
                    # Pad to match header length
                    while len(csv_row) < len(header):
                        csv_row.append("")
                    
                    # Set BOL Cube on first row
                    if bol_cube and csv_row[4] == "":
                        csv_row[4] = bol_cube
                    
                    writer.writerow(csv_row)
        
        print(f"Created CSV for {invoice_no}: {len(all_rows)} rows")

class SimpleCSVExporter:
    """Simplified CSV exporter for API use."""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
    
    def combine_to_csv(self, output_filename: str = "combined_data.csv") -> bool:
        """Combine all CSV files into one."""
        try:
            csv_files = glob.glob(os.path.join(self.working_dir, "*.csv"))
            # Exclude the output file if it already exists
            csv_files = [f for f in csv_files if os.path.basename(f) != output_filename]
            
            if not csv_files:
                print("No CSV files found to combine")
                return False
            
            print(f"Found {len(csv_files)} CSV files to combine")
            
            output_path = os.path.join(self.working_dir, output_filename)
            combined_dfs = []
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file, dtype=str)
                    combined_dfs.append(df)
                    
                    # Clean up individual CSV
                    os.remove(csv_file)
                    print(f"Processed and removed {os.path.basename(csv_file)}")
                    
                except Exception as e:
                    print(f"Error processing {csv_file}: {str(e)}")
                    continue
            
            if combined_dfs:
                # Combine all DataFrames
                final_df = pd.concat(combined_dfs, ignore_index=True)
                
                # Save combined result
                final_df.to_csv(output_path, index=False)
                
                print(f"Successfully combined {len(csv_files)} files into {output_filename}")
                print(f"Total rows: {len(final_df)}")
                
                return True
            else:
                print("No valid CSV data found")
                return False
                
        except Exception as e:
            print(f"Error combining CSV files: {str(e)}")
            return False

class SimpleBOLProcessor:
    """Complete BOL processing pipeline."""
    
    @staticmethod
    def process_bol(pdf_content: bytes, pdf_filename: str, 
                   csv_content: Optional[bytes] = None, 
                   csv_filename: Optional[str] = None) -> bytes:
        """Process BOL PDF and optional CSV, return final CSV content."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Step 1: Save PDF and process
                pdf_path = os.path.join(temp_dir, pdf_filename)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                
                pdf_processor = SimplePDFProcessor(temp_dir)
                if not pdf_processor.process_pdf(pdf_path):
                    raise Exception("PDF processing failed")
                
                # Step 2: Process extracted text
                data_processor = SimpleDataProcessor(temp_dir)
                if not data_processor.process_all_files():
                    raise Exception("Data processing failed")
                
                # Step 3: Create CSV
                csv_exporter = SimpleCSVExporter(temp_dir)
                if not csv_exporter.combine_to_csv():
                    raise Exception("CSV creation failed")
                
                # Step 4: Merge additional CSV if provided
                final_csv_path = os.path.join(temp_dir, "combined_data.csv")
                
                if csv_content and csv_filename:
                    # Save and merge additional CSV
                    additional_csv_path = os.path.join(temp_dir, csv_filename)
                    with open(additional_csv_path, 'wb') as f:
                        f.write(csv_content)
                    
                    # Simple merge
                    base_df = pd.read_csv(final_csv_path, dtype=str)
                    
                    if csv_filename.lower().endswith('.csv'):
                        additional_df = pd.read_csv(additional_csv_path, dtype=str)
                    else:
                        additional_df = pd.read_excel(additional_csv_path, dtype=str)
                    
                    # Basic concatenation merge
                    merged_df = pd.concat([base_df, additional_df], ignore_index=True)
                    merged_df.to_csv(final_csv_path, index=False)
                
                # Step 5: Return final CSV content
                with open(final_csv_path, 'rb') as f:
                    return f.read()
                
            except Exception as e:
                raise Exception(f"BOL processing failed: {str(e)}")

# Export main classes
__all__ = [
    'SimplePDFProcessor',
    'SimpleDataProcessor', 
    'SimpleCSVExporter',
    'SimpleBOLProcessor'
] 