from tkinter import filedialog
import pdfplumber
from duckle_parser import BankStatementParser
from database_handler import DatabaseHandler

class FileHandler:
    def __init__(self, parser, db_handler):
        self.parser = parser
        self.db_handler = db_handler

    def load_pdf(self):
        """Opens a file dialog and processes the selected PDF."""
        pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not pdf_file_path:
            print("No file selected.")
            return None

        try:
            with pdfplumber.open(pdf_file_path) as pdf:
                all_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

            if not all_text.strip():
                print("No text found, attempting OCR...")
                all_text = self.parser.perform_ocr_on_pdf(pdf_file_path)

            # Return the raw text instead of parsed transactions
            return all_text

        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return None


