import pdfplumber
from tkinter import filedialog
from duckle_parser import process_pdf  # Ensure this matches the correct filename

class FileHandler:
    def __init__(self, parser):
        self.parser = parser  # Use the parser instance

    def load_pdf(self):
        """Opens a file dialog and processes the selected PDF."""
        pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not pdf_file_path:
            print("No file selected.")  # Debugging step
            return None

        print(f"Selected file: {pdf_file_path}")  # Debugging step

        try:
            with pdfplumber.open(pdf_file_path) as pdf:
                all_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"

            if all_text.strip():
                print("Extracted Text from PDF:")
                print(all_text[:500])  # Print only the first 500 characters for debugging
                return all_text
            else:
                print("No text found, attempting OCR...")  # Debugging step
                ocr_text = self.parser.perform_ocr_on_pdf(pdf_file_path)
                print("OCR Extracted Text:")
                print(ocr_text[:500])  # Print a portion of the extracted text
                return ocr_text

        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return None
